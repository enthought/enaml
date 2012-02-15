import numpy as np


class  BufferOp(object):
    def __init__(self, sample_probability=1.0, sample_fn=None, pass_through=True):
        self.sample_probability = sample_probability
        self.sample_fn = sample_fn
        self.pass_through = pass_through

    def sample(self, data):
        if self.pass_through:
            buffer = data
        elif self.sample_fn:
            buffer = self.sample_fn(data)
        else:
            num_entries = data.shape[0]
            coin_flips = np.random.random(num_entries)
            mask = coin_flips < self.sample_probability
            buffer = np.copy(data[mask])
        return buffer
