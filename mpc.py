import random, time
from rpc.src import *

def mp(a, b):
    x = a[0] + b[0] * a[1]
    y = a[1] * b[1]
    return (x, y)

def ss(x):
    a = random.random() * x
    return (a, x-a)

def sim_mpc(x, y, s, c):
    x = ss(x)
    y = ss(y)
    g = mp(x, y)
    p = (x[0] + y[0], x[1] + y[1])
    l = 32
    while l > 0:
        for _ in range(l):
            mp(g, p)
            m = {
                'a': g,
                'v': p,
            }
        c.send(s, m)
        l >>= 1
    mp(g, p)

def sim_mpc_n(n):
    st = time.time()
    ys = []
    s = Grpcer()
    s.start_server(lambda x: None)
    c = Grpcer()
    for _ in range(n):
        for _ in range(2):
            x = random.random() * 123
            y = random.random() * 123
            sim_mpc(x, y, s, c)
        ys.append(time.time()-st)
    return ys