from pathlib import Path


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
