from calendar import c
import nacl.encoding
import nacl.hash
import random

from utils import *

def bin_enc(x):
    res = bin(abs(x))[2:]
    n = len(res)
    if x < 0:
        return '0' + '1' * (64 - n - 1) + ''.join(['1' if i=='0' else '0' for i in res])
    return '1' + '0' * (64 - n - 1) + res


def prg(sd):
    random.seed(sd)
    return random.randint(1, 123580)


class OREncoding:
    def __init__(self, x) -> None:
        self.x = x
    
    def __eq__(self, __o) -> bool:
        return self.x == __o.x

    def __lt__(self, __o):
        return ORE.compare(self, __o) == -1

    def __gt__(self, __o):
        return ORE.compare(self, __o) == 1
    
    def __ge__(self, __o):
        return ORE.compare(self, __o) != -1

    def __str__(self) -> str:
        return str(self.x)

class ORE:
    def __init__(self, key='111'):
        self.key = key
        self.hasher = nacl.hash.blake2b
    
    def encode(self, x: int):
        res = 0
        s = bin_enc(x)
        n = len(s)
        for i in range(63, -1, -1):
            # t = f'{self.key}{i}{s[:i]}{"0" * (n-i)}'.encode()
            # digest = self.hasher(t, encoder=nacl.encoding.HexEncoder)
            t = int(f'{self.key}{i}{s[:i]}{"0" * (n-i)}')
            res = (res << 2) | ((prg(t) + int(s[i])) & 0b11)
        return OREncoding(res)

    @staticmethod
    def compare(x: OREncoding, y: OREncoding):
        if x == y:
            return 0
        _x = x.x
        _y = y.x
        for _ in range(64):
            a = _x & 0b11
            b = _y & 0b11
            if a != b:
                return 1 if a == (b+1) & 0b11 else -1
            _x >>= 2
            _y >>= 2
