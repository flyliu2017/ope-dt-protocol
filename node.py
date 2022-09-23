import imp
from ore import *
from bplustree import *

class Coordinator:
    def __init__(self):
        self.tree = BPlusTree(order=32)

    def encode(self, arr):
        for i in arr:
            self.tree.insert(key=i, val=0)

    def calc_encoding(self):
        pass


class ModelProvider:
    def __init__(self):
        pass

class DataOwner:
    def __init__(self):
        pass
