import argparse
import json
import os.path
import pickle
import random
import time

from sklearn.metrics import accuracy_score

from node import ModelProvider, Coordinator, DataOwner
from ore import OREncoding
from rpc.src.grpc import GrpcClient, GrpcServer
import logging

from utils import scale_val

logging.basicConfig(level=logging.INFO)


class OPEDTCoordinator:
    def __init__(self, ip, port, data_owner_num=1):
        self.co = Coordinator()
        self.logger = logging.getLogger(self.__class__.__name__)

        self.data_owner_num = data_owner_num

        self.server = GrpcServer(callback=self.receive_encoded_data, addr=ip, port=port, yml=False)
        self.server.start_server()
        self.logger.info('coordinator grpc server started.')

        self.mp_arr = None
        self.encoded_data = [[]] * self.data_owner_num
        self.receive_mp = False
        self.receive_count = 0
        self.send_back_count = 0

    def receive_encoded_data(self, data):
        data = pickle.loads(data)
        if isinstance(data, dict):
            if data['type'] == 'mp':
                self.mp_arr = data['data']
                self.logger.info("receive data from mp.")
                self.receive_mp = True
            else:
                self.encoded_data[data['index']] = data['data']
                self.logger.info("receive data from data owner {}.".format(data['index']))
                self.receive_count += 1
        else:
            raise ValueError('Wrong data : {}'.format(data))

        while self.receive_count != self.data_owner_num or not self.receive_mp:
            time.sleep(1)

        do_arr = []
        for n in self.encoded_data:
            do_arr.extend(n)
        self.co.receive_keys(self.mp_arr, do_arr)
        result = self.co.mp_map if data['type'] == 'mp' else self.co.do_map
        self.logger.info("send map to {}".format(data['type']))
        self.send_back_count += 1
        return pickle.dumps(result)

    def run(self):
        while self.send_back_count != self.data_owner_num + 1 or not self.receive_mp:
            time.sleep(2)
        time.sleep(2)
        self.server.close_server()


class OPEDTModelProvider:
    def __init__(self, model_path, ip, port, co_ip, co_port, data_owner_num=1):
        self.mp = ModelProvider()
        self.logger = logging.getLogger(self.__class__.__name__)

        self.sk = str(random.randint(0, 1000))
        self.mp.ore.key = self.sk
        self.mp.load_model(model_path)

        self.data_owner_num = data_owner_num
        self.co_port = co_port
        self.co_ip = co_ip

        self.co_client = GrpcClient(yml=False)
        self.do_server = GrpcServer(callback=self.receive_encoded_data, addr=ip, port=port, yml=False)
        self.do_server.start_server()
        self.logger.info('model provider grpc server started.')

        self.encoded_data = [[]] * data_owner_num
        self.receive_count = 0

    def receive_encoded_data(self, data):
        data = pickle.loads(data)
        if isinstance(data, str):
            return pickle.dumps(self.sk)
        elif isinstance(data, dict):
            index = data['index']
            encoded_data = data['data']
            self.encoded_data[index] = encoded_data
            self.logger.info("receive data from data owner {}.".format(data['index']))
            self.receive_count += 1
        else:
            raise ValueError('Wrong data : {}'.format(data))

    def run(self):
        mp_encs = self.mp.get_encodings()
        self.logger.info("send encoded data to coordinator.")
        map = self.co_client.send([self.co_ip, self.co_port], pickle.dumps({'type': 'mp', 'data': mp_encs}))
        self.logger.info("receive map from coordinator.")
        self.mp.receive_map(pickle.loads(map))

        while self.receive_count != self.data_owner_num:
            time.sleep(2)

        num = len(self.encoded_data[0])
        data = []
        for i in range(num):
            new = []
            for l in self.encoded_data:
                new.extend(l[i])
            data.append(new)

        labels = [l[-1] for l in data]
        prediction = self.mp.encoded_model.predict([l[:-1] for l in data])
        encode_prediction = []
        for n in prediction:
            _v = self.mp.ore.encode(scale_val(n))
            encode_prediction.append(_v)

        correct = 0
        for n1, n2 in zip(encode_prediction, labels):
            if n1 == n2:
                correct += 1
        score = correct / len(prediction)
        print(f'ACC: {score * 100:.2f}%')
        return prediction


class OPEDTDataOwner:
    def __init__(self, data_path, index, mp_ip, mp_port, co_ip, co_port, data_owner_num=1):
        self.data_owner = DataOwner(data_path)
        self.index = index
        self.logger = logging.getLogger(self.__class__.__name__)
        self.has_label = self.index + 1 == data_owner_num

        self.mp_ip = mp_ip
        self.mp_port = mp_port
        self.co_port = co_port
        self.co_ip = co_ip

        self.co_client = GrpcClient(yml=False)
        self.mp_client = GrpcClient(yml=False)

    def run(self):
        sk = self.mp_client.send([self.mp_ip, self.mp_port], pickle.dumps('request key'))
        self.logger.info("receive secret key from mp.")
        self.data_owner.ore.key = pickle.loads(sk)

        encs = self.data_owner.get_encodings()
        self.logger.info("send encoded data to coordinator.")
        map = self.co_client.send([self.co_ip, self.co_port], pickle.dumps({'type': 'do',
                                                                            'index': self.index,
                                                                            'data': encs}))
        self.logger.info("receive map from coordinator.")
        self.data_owner.receive_map(pickle.loads(map))

        self.mp_client.send([self.mp_ip, self.mp_port], pickle.dumps({'index': self.index,
                                                                      'data': self.encode_dataset()}))
        self.logger.info("send encoded data to model provider.")

    def encode_dataset(self):
        enc_dataset = []
        for sample in self.data_owner.dataset:
            _s = sample[:-1]
            for i in range(len(_s)):
                _v = self.data_owner.ore.encode(scale_val(_s[i])).x
                _s[i] = OREncoding(self.data_owner.ore_map[_v])
            if self.has_label:
                _s.append(self.data_owner.ore.encode(scale_val(sample[-1])))
            enc_dataset.append(_s)
        return enc_dataset


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--role', type=str, choices=['mp', 'co', 'do'], required=True)
    parser.add_argument('--index', type=int, default=0)
    parser.add_argument('--model_path', type=str, default='')
    parser.add_argument('--data_path', type=str, default='')
    args = parser.parse_args()

    class_dict = {
        "mp": OPEDTModelProvider,
        "co": OPEDTCoordinator,
        "do": OPEDTDataOwner,
    }
    config = json.load(open('config.json'))
    co_ip = config['co_ip']
    co_port = config['co_port']
    mp_ip = config['mp_ip']
    mp_port = config['mp_port']
    data_owner_list = config['data_owners']
    data_owner_num = len(data_owner_list)

    role = args.role
    if role == 'co':
        OPEDTCoordinator(ip=co_ip, port=co_port, data_owner_num=data_owner_num).run()
    elif role == 'mp':
        assert args.model_path
        OPEDTModelProvider(model_path=args.model_path, ip=mp_ip, port=mp_port,
                           co_ip=co_ip, co_port=co_port, data_owner_num=data_owner_num).run()
    else:
        assert args.data_path
        OPEDTDataOwner(data_path=args.data_path, index=args.index,
                       mp_ip=mp_ip, mp_port=mp_port, co_ip=co_ip, co_port=co_port, data_owner_num=data_owner_num).run()
