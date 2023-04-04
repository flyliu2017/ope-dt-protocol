import random
import time
import pickle
from tqdm.auto import tqdm

from trans import TransDT
from ore import *
from bplustree import *
from read_data import *
from sklearn.tree import DecisionTreeClassifier
from sklearn.datasets import load_svmlight_file


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
            res.append(time.time() - st)
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
        self.model = None
        self.encoded_model = None
    def train_model(self, data_path):
        self.x, self.y = load_svmlight_file(data_path)
        self.model = DecisionTreeClassifier(max_depth=3)
        self.model.fit(self.x, self.y)
        score = self.model.score(self.x, self.y)
        print(f'MP model score: {score * 100:.2f}%')

    def load_model(self, model_path):
        self.model = pickle.load(open(model_path, 'rb'))

    def get_encodings(self):
        res = []
        model = self.model.tree_
        for i in range(model.node_count):
            if model.children_left[i] != model.children_right[i]:
                res.append(scale_val(model.threshold[i]))
        res = [self.ore.encode(x) for x in res]
        return res

    def encode_threshold_by_map(self, tree):
        threshold_list = tree.threshold.tolist()
        encode_result = []
        for i in range(tree.node_count):
            if tree.children_left[i] != tree.children_right[i]:
                _k = threshold_list[i]
                _k = self.ore.encode(scale_val(_k)).x
                encode_result.append(OREncoding(self.ore_map[_k]))
            else:
                encode_result.append(threshold_list[i])
        print('All val in tree are mapped to OREncoding.')
        return encode_result
    def receive_map(self, ore_map):
        self.ore_map = ore_map
        self.trans_model()

    def trans_model(self):
        if self.encoded_model is None:
            n_nodes = self.model.tree_.node_count
            children_left = self.model.tree_.children_left.tolist()
            children_right = self.model.tree_.children_right.tolist()
            feature = self.model.tree_.feature.tolist()
            values = self.model.tree_.value.tolist()

            classes = self.model.classes_

            def get_cls(s):
                idx = max(list(enumerate(s)), key=lambda x: x[1])[0]
                return classes[idx]

            values = [get_cls(s[0]) for s in values]
            threshold = self.encode_threshold_by_map(self.model.tree_)

            ret = TransDT()
            ret.n_nodes = n_nodes
            ret.children_left = children_left
            ret.children_right = children_right
            ret.feature = feature
            ret.threshold = threshold
            ret.values = values

            self.encoded_model = ret
        return ret


class DataOwner:
    def __init__(self, data_path):
        self.dataset = read_libsvm(data_path)
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
