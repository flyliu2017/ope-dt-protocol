class TransDT:
    def __init__(self) -> None:
        pass

    def is_leaf(self, s):
        return self.children_left[s] == self.children_right[s]

    def predict_single(self, sample):
        now = 0
        while not self.is_leaf(now):
            tar = sample[self.feature[now]]
            if tar <= self.threshold[now]:
                now = self.children_left[now]
            else:
                now = self.children_right[now]
        return self.values[now]
    
    def predict(self, xs):
        return [self.predict_single(x) for x in xs]


def trans_sk_model(model):
    n_nodes = model.tree_.node_count
    children_left = model.tree_.children_left.tolist()
    children_right = model.tree_.children_right.tolist()
    feature = model.tree_.feature.tolist()
    threshold = model.tree_.threshold.tolist()
    values = model.tree_.value.tolist()

    classes = model.classes_
    def get_cls(s):
        idx = max(list(enumerate(s)), key=lambda x: x[1])[0]
        return classes[idx]
    values = [get_cls(s[0]) for s in values]

    ret = TransDT()
    ret.n_nodes = n_nodes
    ret.children_left = children_left
    ret.children_right = children_right
    ret.feature = feature
    ret.threshold = threshold
    ret.values = values

    return ret
