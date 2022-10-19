import random

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
        for key in mp_arr + do_arr:
            self.tree.insert(key=key, val=0)
        node = self.tree.get_left_leaf()
        cnt = 0
        while node is not None:
            for i, k in enumerate(node.keys):
                node.vals[i] = cnt
                cnt += 1
            node = node.next
        print('All data inserted into tree.')
        self.calc_encoding()

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
        self.dataset = read_iris()
        self.model = CartTree(max_depth=3)
        self.model.fit(self.dataset)
        score = self.model.score(self.dataset, [x[-1] for x in self.dataset])
        print(f'MP model score: {score * 100:.2f}%')

    def get_encodings(self):
        res = []
        def dfs(node):
            if node.label is not None:
                return
            res.append(scale_val(node.val))
            for nd in node.children:
                dfs(nd)
        dfs(self.model.root)
        res = [self.ore.encode(x) for x in res]
        return res

    def receive_map(self, ore_map):
        self.ore_map = ore_map
        def dfs(node):
            if node.label is not None:
                return
            _k = self.ore.encode(scale_val(node.val)).x
            node.ori_val = node.val
            node.val = OREncoding(ore_map[_k])
            for nd in node.children:
                dfs(nd)
        dfs(self.model.root)
        print('All val in tree are mapped to OREncoding.')
        self.model.save_plot()


class DataOwner:
    def __init__(self):
        self.dataset = read_iris()
        self.ore = ORE()

    def get_encodings(self):
        res = []
        for sample in self.dataset:
            for v in sample:
                if isinstance(v, float) or isinstance(v, int):
                    res.append(scale_val(v))
        res = [self.ore.encode(x) for x in res]
        return res

    def receive_map(self, ore_map):
        self.ore_map = ore_map
