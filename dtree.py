from collections import Counter
from sklearn.metrics import accuracy_score

def gini(arr):
    counter = Counter(arr)
    res, n = 1.0, len(arr)
    for num in counter.values():
        p = num / n
        res -= p**2
    return res


class CartNode:
    def __init__(self, kv=None, children=None, label=None):
        if kv is not None:
            self.key = int(kv[0])
            self.val = kv[1]
        else:
            self.kv = None
        self.children = children
        self.label = label


class CartTree:
    def __init__(self, min_gain=0.8):
        self.min_gain = min_gain

    def fit(self, samples):
        '''
            samples: list of samples, sample[-1] is label
        '''
        self.root = self.build(samples)

    @staticmethod
    def split(samples, key, val):
        left = []
        right = []
        for i, sample in enumerate(samples):
            if sample[key] >= val:
                right.append(i)
            else:
                left.append(i)
        return left, right

    @staticmethod
    def build(samples):
        labels = [x[-1] for x in samples]
        cur_gini  = gini(labels)
        n = len(samples)

        best_gain = 0.
        best_split = None
        best_lr = None

        n_feature = len(samples[0]) - 1 
        for i in range(n_feature):
            vals = set(x[i] for x in samples)
            for v in vals:
                lid, rid = CartTree.split(samples, i, v)
                p = float(len(lid)) / n
                lx = [labels[j] for j in lid]
                rx = [labels[j] for j in rid]
                gain = cur_gini - p * gini(lx) - (1-p) * gini(rx)
                if gain > best_gain and len(lx) and len(rx):
                    best_gain = gain
                    best_split = (i, v)
                    best_lr = (lid, rid)

        if best_gain > 0:
            lx = [samples[i] for i in best_lr[0]]
            rx = [samples[i] for i in best_lr[1]]
            return CartNode(kv=best_split, 
                            children=[CartTree.build(lx), 
                                      CartTree.build(rx)])
        else:
            _c = Counter(labels)
            label = max(_c, key=_c.get)
            return CartNode(label=label)

    @staticmethod
    def predict_single(node, x):
        if node.label is not None:
            return node.label
        if x[node.key] >= node.val:
            return CartTree.predict_single(node.children[1], x)
        else:
            return CartTree.predict_single(node.children[0], x)

    def predict(self, xs):
        return [self.predict_single(self.root, x) for x in xs]

    def score(self, xs, ys):
        res = self.predict(xs)
        return accuracy_score(res, ys)
