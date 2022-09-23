MAXN  = 1 << 64
SCALE = 1 << 32

def scale_val(x):
    res = int(x * SCALE)
    if abs(res) >= MAXN:
        raise Exception('Beyond MAXN!')
    return res

