import os.path
import pickle
import random

from sklearn.metrics import accuracy_score

from node import Coordinator, DataOwner, ModelProvider
from ore import OREncoding
from utils import scale_val
from read_data import DATA_PATH


def simulate():
    iris_data = os.path.join(DATA_PATH, 'iris.libsvm')
    co = Coordinator()
    do = DataOwner(iris_data)
    mp = ModelProvider()
    mp.train_model(iris_data)
    # pickle.dump(mp.model, open('model/iris_model.pickle', 'wb'))

    key_0 = str(random.randint(0, 1000))
    do.ore.key = key_0
    mp.ore.key = key_0
    do_encs = do.get_encodings()
    mp_encs = mp.get_encodings()
    co.receive_keys(mp_arr=mp_encs, do_arr=do_encs)

    mp.receive_map(co.mp_map)
    do.receive_map(co.do_map)

    enc_dataset = []
    for sample in do.dataset:
        _s = sample[:]
        for i in range(len(_s)-1):
            _v = do.ore.encode(scale_val(_s[i])).x
            _s[i] = OREncoding(do.ore_map[_v])
        enc_dataset.append(_s)

    ys = [x[-1] for x in enc_dataset]
    pred = mp.encoded_model.predict(enc_dataset)
    print(f'ACC: {accuracy_score(pred, ys) * 100:.2f}%')

if __name__ == '__main__':
    simulate()