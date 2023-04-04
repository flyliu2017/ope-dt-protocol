from concurrent import futures
import grpc
import yaml

from .base import *
from .proto import *


class GrpcService(bytes_pb2_grpc.BytesServicer):
    def __init__(self, master=None, yml=True):
        self.master = master
        self.yml = yml
        self.msg_queue = []

    def send(self, request, context):
        msg = request.msg
        if self.master.callback is not None:
            if self.yml:
                msg = yaml.safe_load(msg)

            res = self.master.callback(msg)

            if self.yml and not isinstance(res, bytes):
                res = yaml.safe_dump(res).encode()
            return bytes_pb2.Res(res=res)
        return bytes_pb2.Res(res=''.encode())


class GrpcServer:
    def __init__(self, callback=None, addr='localhost', port=None, yml=True):
        self.yml = yml
        self.callback = callback
        self.addr = addr
        self.port = port
        self.server_credentials = None

    def start_server(self, key_pem_file=None, chain_pem_file=None):
        self.rpc_service = GrpcService(master=self, yml=self.yml)
        self.rpc_server = grpc.server(futures.ThreadPoolExecutor(max_workers=4))
        bytes_pb2_grpc.add_BytesServicer_to_server(self.rpc_service, self.rpc_server)
        if self.port is None:
            self.port = get_free_port()

        if key_pem_file is None:
            self.rpc_server.add_insecure_port(f'[::]:{self.port}')
        else:
            with open(key_pem_file, 'rb') as f:
                private_key = f.read()
            with open(chain_pem_file, 'rb') as f:
                certificate = f.read()
            self.server_credentials = grpc.ssl_server_credentials(((private_key, certificate,),))
            self.rpc_server.add_secure_port(f'[::]:{self.port}', self.server_credentials)
        self.rpc_server.start()

    def close_server(self):
        self.rpc_server.stop()


class GrpcClient:
    def __init__(self, yml=True):
        self.yml = yml
        self.conns = {}

    def send(self, target, msg):
        if isinstance(target, dict):
            addr, port = target['addr'], target['port']
        elif isinstance(target, (list, tuple)):
            addr, port = target
        elif isinstance(target, RpcerBase):
            addr, port = target.addr, target.port
        else:
            raise Exception('Unrecognizable target.')

        ap = f'{addr}:{port}'
        if ap not in self.conns:
            ch = grpc.insecure_channel(ap)
            self.conns[ap] = bytes_pb2_grpc.BytesStub(ch)

        if self.yml:
            msg = yaml.safe_dump(msg).encode()
        res = self.conns[ap].send(bytes_pb2.Msg(msg=msg)).res
        if self.yml:
            res = yaml.safe_load(res)
        return res


class Grpcer(RpcerBase):
    def __init__(self, yml=True):
        super().__init__()
        self.yml = yml
        self.client = GrpcClient(yml=self.yml)

    def start_server(self, callback=None, addr='localhost', port=None, key_pem_file=None, chain_pem_file=None):
        self.server = GrpcServer(callback=callback, addr=addr, port=port, yml=self.yml)
        self.server.start_server(key_pem_file=key_pem_file, chain_pem_file=chain_pem_file)

    def send(self, target, msg):
        return self.client.send(target, msg)
    