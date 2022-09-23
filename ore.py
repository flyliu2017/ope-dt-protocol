import nacl.encoding
import nacl.hash

from utils import *

def bin_enc(x):
    res = bin(abs(x))[2:]
    n = len(res)
    if x < 0:
        return '0' + '1' * (64 - n - 1) + ''.join(['1' if i=='0' else '0' for i in res])
    return '1' + '0' * (64 - n - 1) + res

class ORE:
    def __init__(self, key):
        self.key = key
        self.hasher = nacl.hash.sha256
    
    def encode(self, x: int):
        res = 0
        s = bin_enc(x)
        n = len(s)
        for i in range(63, -1, -1):
            t = f'{self.key}{i}{s[:i]}{"0" * (n-i)}'.encode()
            digest = self.hasher(t, encoder=nacl.encoding.HexEncoder)
            res = (res << 2) | ((int.from_bytes(digest, 'big') + int(s[i])) & 0b11)
        return res

    def compare(self, x: int, y: int):
        if x == y:
            return 0
        for i in range(64):
            a = x & 0b11
            b = y & 0b11
            if a != b:
                return 1 if a == (b+1) & 0b11 else -1
            x >>= 2
            y >>= 2
