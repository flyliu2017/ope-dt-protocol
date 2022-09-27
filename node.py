import random

from utils import *
from ore import *
from bplustree import *

class Coordinator:
    def __init__(self):
        self.tree = BPlusTree(order=32)
        self.ore = ORE(key=str(random.randint(1, 1000)))

    def encode(self, arr):
        for i in arr:
            self.tree.insert(key=i, val=0)

    def receive_keys(self, mo_arr, do_arr):
        self.mo_arr = mo_arr
        self.do_arr = do_arr
        for key in mo_arr + do_arr:
            self.tree.insert(key=key, val=0)
        node = self.tree.get_left_leaf()
        cnt = 0
        while node is not None:
            for i, k in enumerate(node.keys):
                node.vals[i] = cnt
                cnt += 1
            node = node.next
        logger.info('All data inserted into tree.')
        self.calc_encoding()

    def calc_encoding(self):
        self.mo_map = {}
        self.do_map = {}
        for key in self.mo_arr:
            self.mo_map[key.x] = self.ore.encode(self.tree.find(key)).x
        for key in self.do_arr:
            self.mo_map[key.x] = self.ore.encode(self.tree.find(key)).x
        logger.info('All data mapped to encoding.')

class ModelProvider:
    def __init__(self):
        pass

class DataOwner:
    def __init__(self):
        pass
