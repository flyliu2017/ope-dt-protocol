import websockets
import asyncio
import threading
import yaml
import queue
from collections import defaultdict

from .base import *
from .proto import *


class WsServer:
    def __init__(self, callback=None, addr='localhost', port=None):
        self.callback = callback
        self.addr = addr
        self.port = port

    async def echo(self, websocket):
        async for msg in websocket:
            msg = yaml.safe_load(msg)
            res = self.callback(msg)
            res = yaml.safe_dump(res)
            await websocket.send(res)

    async def start_listen(self):
        async with websockets.serve(self.echo, self.addr, self.port):
            print(f'Start at {self.addr}:{self.port}.')
            await asyncio.Future()

    def start_server(self):
        if self.port is None:
            self.port = get_free_port()
        self.server_thread = threading.Thread(
            target=lambda: asyncio.run(self.start_listen()))
        self.server_thread.start()


class WsClient:
    def __init__(self):
        self.conns = {}
        self.msg_queue = {}
        self.res_queue = {}
        self.qid = 0

    def create_conn(self, name, addr, port):
        if name not in self.conns:
            self.conns[name] = threading.Thread(
                target=lambda: asyncio.run(self._send(addr, port, name)),
                # kwargs={'addr': addr, 'port': port, 'name': name}
            )
            self.msg_queue[name] = queue.Queue()
            self.res_queue[name] = defaultdict(lambda: None)
            # self.msg_queue[name].put({"cmd": "handshake"})
            self.conns[name].start()

    def send(self, name, msg):
        if name in self.conns:
            now = self.qid
            self.qid = (self.qid + 1) % 65535
            self.msg_queue[name].put((msg, now))
            while self.res_queue[name][now] is None:
                pass
            res = self.res_queue[name][now]
            self.res_queue[name][now] = None
            return res

    async def _send(self, addr, port, name):
        tar = f'{addr}:{port}'
        async with websockets.connect(f"ws://{tar}") as websocket:
            while True:
                if not self.msg_queue[name].empty():
                    msg, now = self.msg_queue[name].get()
                    await websocket.send(yaml.safe_dump(msg))
                    res = await websocket.recv()
                    self.res_queue[name][now] = yaml.safe_load(res)


class Wser(RpcerBase):
    def __init__(self):
        super().__init__()
        self.client = WsClient()

    def start_server(self, callback, addr='0.0.0.0', port=None):
        self.server = WsServer(callback=callback, addr=addr, port=port)
        self.server.start_server()

    def send(self, target, msg):
        return self.client.send(target, msg)
    