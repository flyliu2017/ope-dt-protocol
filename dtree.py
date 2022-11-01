from asyncio.log import logger
from collections import Counter
from queue import Queue
from re import S
from sklearn.metrics import accuracy_score
import pydotplus as pdp


def gini(arr):
    counter = Counter(arr)
    res, n = 1.0, len(arr)
    for num in counter.values():
        p = num / n
        res -= p**2
    return res


IRIS_FEATURE = ['Sepal length', 'Sepal width', 'Petal length', 'Petal width']

class CartNode:
    def __init__(self, kv=None, children=None, label=None, depth=0):
        if kv is not None:
            self.key = int(kv[0])
            self.val = kv[1]
        else:
            self.kv = None
        self.children = children
        self.label = label
        self.depth = depth

    def get_plot_text(self):
        if self.label is not None:
            return f"{self.label}"
        # return f'{IRIS_FEATURE[self.key]} < {self.val}?'
        try:
            return f'{IRIS_FEATURE[self.key]} < {self.ori_val}?\n=>\n{IRIS_FEATURE[self.key]} < ..{str(self.val)[-4:]}'
        except:
            return f'{IRIS_FEATURE[self.key]} < {self.val}?'

class CartTree:
    def __init__(self, min_gain=0.8, max_depth=18):
        self.min_gain = min_gain
        self.max_depth = max_depth

    def fit(self, samples):
        '''
            samples: list of samples, sample[-1] is label
        '''
        self.root = self.build(samples, depth=0)

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

    def build(self, samples, depth=0):
        labels = [x[-1] for x in samples]
        cur_gini  = gini(labels)
        n = len(samples)

        if depth < self.max_depth:
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
                                children=[self.build(lx, depth=depth+1), 
                                        self.build(rx, depth=depth+1)],
                                depth=depth)
        _c = Counter(labels)
        label = max(_c, key=_c.get)
        return CartNode(label=label, depth=depth)

    def predict_single(self, x):
        node = self.root
        while node.label is None:
            if x[node.key] >= node.val:
                node = node.children[1]
            else:
                node = node.children[0]
        return node.label

    def predict(self, xs):
        return [self.predict_single(x) for x in xs]

    def score(self, xs, ys):
        res = self.predict(xs)
        return accuracy_score(res, ys)

    def bfs_get_id(self):
        q = Queue()
        q.put(self.root)
        cnt = 0
        res = ''
        while not q.empty():
            now = q.get()
            now.name = f'a{cnt}'
            res += f'{now.name}[label="{now.get_plot_text()}"] ;'
            cnt += 1
            if now.children is not None:
                for c in now.children:
                    q.put(c)
        return res

    def save_plot(self):
        plot_str = self.bfs_get_id()
        q = Queue()
        q.put(self.root)
        while not q.empty():
            now = q.get()
            if now.children is not None:
                for c in now.children:
                    q.put(c)
                    plot_str += f'{now.name} -> {c.name}; '
        plot_str = 'digraph g {%s}' % plot_str
        # logger.info(f'plot_str: {plot_str}')
        # graph = pdp.graph_from_dot_data(plot_str)
        # open('img/tree.png', 'wb').write(graph.create_png())
        # graph.write('img/tree.eps', format='eps')