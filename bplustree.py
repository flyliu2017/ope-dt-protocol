import bisect
from queue import Queue

class Node:
    def __init__(self, parent=None, is_leaf=False):
        self.parent = parent
        self.is_leaf = is_leaf
        self.keys = []
        self.vals = []
        self.prev = self.next = None

    @property
    def is_root(self):
        return self.parent is None

    def find(self, key):
        if not self.keys:
            return None
        i = bisect.bisect_left(self.keys, key)
        if not self.is_leaf:
            if i >= len(self.keys):
                return self.vals[-1]
            elif key < self.keys[i]:
                return self.vals[i]
            else:
                return self.vals[i+1]
        else:
            if i >= len(self.keys) or self.keys[i] != key:
                return None
            return self.vals[i]

    def split(self):
        if self.is_leaf:
            lson = Node(parent=self, is_leaf=True)
            rson = Node(parent=self, is_leaf=True)
            self.is_leaf = False
            
            mid = len(self.keys) >> 1
            
            lson.keys = self.keys[:mid]
            lson.vals = self.vals[:mid]
            rson.keys = self.keys[mid:]
            rson.vals = self.vals[mid:]
            self.keys = [self.keys[mid]]
            self.vals = [lson, rson]
            
            try:
                self.prev.next = lson
            except:
                pass
            try:
                self.next.prev = rson
            except:
                pass
            lson.next = rson
            rson.prev = lson
            lson.prev = self.prev
            rson.next = self.next
            self.prev = self.next = None
        else:
            lson = Node(parent=self)
            rson = Node(parent=self)
            mid = len(self.keys) >> 1

            lson.keys = self.keys[:mid]
            lson.vals = self.vals[:mid + 1]
            rson.keys = self.keys[mid+1:]
            rson.vals = self.vals[mid+1:]
            self.keys = [self.keys[mid]]
            self.vals = [lson, rson]

            for node in lson.vals:
                node.parent = lson
            for node in rson.vals:
                node.parent = rson


    def insert(self, key, val):
        if not self.is_leaf:
            return
        if not self.keys:
            self.keys.append(key)
            self.vals.append(val)
            return
        for i, k in enumerate(self.keys):
            if k == key:
                self.vals[i] = val
                return

            elif key < k:
                self.keys = self.keys[:i] + [key] + self.keys[i:]
                self.vals = self.vals[:i] + [val] + self.vals[i:]
                return
        
        self.keys.append(key)
        self.vals.append(val)


class BPlusTree:
    def __init__(self, order) -> None:
        self.order = order
        self.root = Node(is_leaf=True)

    def find(self, key):
        now = self.root
        while not now.is_leaf:
            now = now.find(key)
        return now.find(key)

    def merge(self, pa, ch):
        pv = ch.keys[0]
        i = bisect.bisect_left(pa.keys, pv)
        pa.vals.pop(i)
        
        for node in ch.vals:
            node.parent = pa

        for i, k in enumerate(pa.keys):
            if pv < k:
                pa.keys = pa.keys[:i] + [pv] + pa.keys[i:]
                pa.vals = pa.vals[:i] + ch.vals + pa.vals[i:]
                return

        pa.keys.append(pv)
        pa.vals += ch.vals

    def insert(self, key, val):
        now = self.root
        while not now.is_leaf:
            now = now.find(key)
        now.insert(key, val)

        while len(now.keys) >= self.order:
            if now.is_root:
                now.split()
            else:
                pa = now.parent
                now.split()
                self.merge(pa, now)
                now = pa
    
    def bfs(self):
        q = Queue()
        q.put(self.root)
        print('---')
        while not q.empty():
            now = q.get()
            print(f'k: {now.keys}, v: {now.vals}')
            if not now.is_leaf:
                for node in now.vals:
                    q.put(node)
        print('---')
        
    def get_left_leaf(self):
        now = self.root
        while not now.is_leaf:
            now = now.vals[0]
        return now
