from phe import paillier
import random, time
from tqdm.auto import tqdm

def sim_he_n(n):
    pk, sk = paillier.generate_paillier_keypair()
    st = time.time()
    ys = []
    for _ in tqdm(range(n)):
        x = random.random() * 123
        y = random.random() * 123
        _x = pk.encrypt(x)
        _y = pk.encrypt(y)
        _z = _x - _y
        _z *= random.randint(1, 213)
        r = sk.decrypt(_z)
        ys.append(time.time()-st)
    return ys