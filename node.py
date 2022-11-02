import random
import time
import pickle
from tqdm.auto import tqdm

from utils import *
from ore import *
from bplustree import *
from read_data import *
from dtree import *

class Coordinator:
    def __init__(self):
        self.tree = BPlusTree(order=32)
        self.ore = ORE(key=str(random.randint(1, 1000)))

    def encode(self, arr):
        for i in arr:
            self.tree.insert(key=i, val=0)

    def receive_keys(self, mp_arr, do_arr):
        self.mo_arr = mp_arr
        self.do_arr = do_arr
        st = time.time()
        res = []
        for key in tqdm(mp_arr + do_arr):
            self.tree.insert(key=key, val=0)
            res.append(time.time()-st)
        node = self.tree.get_left_leaf()
        cnt = 0
        while node is not None:
            for i, k in enumerate(node.keys):
                node.vals[i] = cnt
                cnt += 1
            node = node.next
        print('All data inserted into tree.')
        self.calc_encoding()
        return res

    def calc_encoding(self):
        self.mp_map = {}
        self.do_map = {}
        for key in self.mo_arr:
            self.mp_map[key.x] = self.ore.encode(self.tree.find(key)).x
        for key in self.do_arr:
            self.do_map[key.x] = self.ore.encode(self.tree.find(key)).x
        print('All data mapped to encoding.')


class ModelProvider:
    def __init__(self):
        self.ore = ORE()

    def train_model(self):
        self.dataset = read_libsvm(name='rna')
        self.model = CartTree(max_depth=3)
        self.model.fit(self.dataset)
        score = self.model.score(self.dataset, [x[-1] for x in self.dataset])
        print(f'MP model score: {score * 100:.2f}%')

    def load_model(self, name='iris', clf='dt'):
        self.model = pickle.load(open(f'model/{name}.{clf}', 'rb'))

    def get_encodings(self):
        res = []
        model = self.model.tree_
        for i in range(model.node_count):
            if model.children_left[i] != model.children_right[i]:
                res.append(scale_val(model.threshold[i]))
        res = [self.ore.encode(x) for x in res]
        return res

    def trans_model(self):
        model = self.model.tree_
        model.threshold = model.threshold.tolist()
        for i in range(model.node_count):
            if model.children_left[i] != model.children_right[i]:
                _k = model.threshold[i]
                _k = self.ore.encode(scale_val(_k)).x
                model.threshold[i] =  OREncoding(self.ore_map[_k])
        print('All val in tree are mapped to OREncoding.')
        
    def receive_map(self, ore_map):
        self.ore_map = ore_map
        self.trans_model()
        # self.model.save_plot()


class DataOwner:
    def __init__(self, dname='iris'):
        self.dataset = auto_read_data(name=dname)
        self.ore = ORE()

    def get_encodings(self):
        res = []
        for sample in self.dataset:
            for v in sample:
                if isinstance(v, float) or isinstance(v, int):
                    res.append(scale_val(v))
        ret = []
        for x in tqdm(set(res)):
            ret.append(self.ore.encode(x))
        return ret

    def receive_map(self, ore_map):
        self.ore_map = ore_map
