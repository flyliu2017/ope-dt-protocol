from collections import Counter
from sklearn.metrics import accuracy_score
import pickle
import random
import math

from utils import *
from dtree import *

class RandomForest:
    def __init__(self, n_tree=100, max_f='sqrt'):
        self.n_tree = n_tree
        self.max_f = max_f
        self.trees = [CartTree() for _ in range(n_tree)]

    def fit(self, samples):
        sample_piece = []
        nf = len(samples[0]) - 1
        if self.max_f == 'sqrt':
            fn = int(math.sqrt(nf))
        elif isinstance(self.max_f, float):
            fn = int(nf * self.max_f)
        print(f'Choose {fn}/{nf} features.')        
        for i in range(self.n_tree):
            sample_piece.append([])
            fs = random.sample(range(nf), fn)
            for s in samples:
                sam = [s[k] for k in fs] + [s[-1]]
                sample_piece[i].append(sam)
        
        print('Start training rf..')
        for i in range(self.n_tree):
            print(f'Training rf {i+1}/{self.n_tree}')
            self.trees[i].fit(sample_piece[i])
        print('End training rf.')

        print('Saving rf.')
        pickle.dump(self, open(f'model/rf.model', 'wb'))
        print('Saving rf done.')
        
    def predict_single(self, x):
        labels = Counter([tree.predict_single(x) for tree in self.trees])
        return labels.most_common(1)[0][0]

    def predict(self, xs):
        return [self.predict_single(x) for x in xs]

    def score(self, xs, ys):
        res = self.predict(xs)
        return accuracy_score(res, ys)
