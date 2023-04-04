from pathlib import Path
from sklearn.datasets import load_svmlight_file

DATA_PATH = Path('./dataset')

def read_iris():
    res = (DATA_PATH / 'iris.data').open(encoding='utf-8').readlines()
    res = [x for x in res if len(x) > 1]
    res = [x.strip().split(',') for x in res]
    nf = len(res[0]) - 1
    for i in range(len(res)):
        for j in range(nf):
            res[i][j] = float(res[i][j])
    return res

def read_rna():
    data = load_svmlight_file(str((DATA_PATH / 'cod-rna.libsvm')))
    xs, ys = data[0], data[1]
    xs = xs.toarray().tolist()
    ys.tolist()
    res = []
    for i in range(len(xs)):
        res.append(xs[i] + [ys[i]])
    return res

def read_libsvm(data_path):
    data = load_svmlight_file(data_path)
    xs, ys = data[0], data[1]
    xs = xs.toarray().tolist()
    ys.tolist()
    res = []
    for i in range(len(xs)):
        res.append(xs[i] + [ys[i]])
    return res

def auto_read_data(name):
    if name in ['rna', 'madelon', 'mushrooms']:
        return read_libsvm(str((DATA_PATH / f'{name}.libsvm')))
    elif name == 'iris':
        return read_iris()