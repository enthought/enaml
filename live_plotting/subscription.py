import threading
from Queue import Queue
import random
import unittest
from abc import ABCMeta, abstractmethod
import time
import numpy as np


class AbstractSubscription(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def start(self):
        raise NotImplementedError

    @abstractmethod
    def stop(self):
        raise NotImplementedError

    @abstractmethod
    def event_loop(self):
        raise NotImplementedError

    @abstractmethod
    def process_feed(self):
        raise NotImplementedError


class Subscription(object):
    def event_loop(self):
        def inner():
            self.process_feed()
            if self.go:
                threading.Timer(self.time_period, inner).start()
        threading.Timer(self.time_period, inner).start()


class ZeroMQSubscription(AbstractSubscription, Subscription):

    def start(self):
        self.go = True

    def stop(self):
        raise NotImplementedError

    def process_feed(self):
        raise NotImplementedError

    def event_loop(self):
        super(Subscription, self).event_loop()


class NumpySubscription(Subscription, AbstractSubscription):

    def __init__(self, data_source, data_feed, sample_probability=1.0, sample_fn=None,
                time_period=1 / 30.0, pass_through=True):
        self.data_source = data_source
        self.data_feed = data_feed
        self.sample_fn = sample_fn
        self.sample_probability = sample_probability
        self.time_period = time_period
        self.pass_through = pass_through
        self.go = True
        self.buffer = None

    def start(self):
        self.go = True
        self.data_feed.start()
        self.event_loop()

    def stop(self):
        self.go = False
        self.data_feed.stop()

    def process_feed(self):
        with self.data_feed.lock:
            valid_slice = np.copy(self.data_feed.valid_slice())
            if self.pass_through:
                buffer = valid_slice
            elif self.sample_fn:
                buffer = self.sample_fn(valid_slice)
            else:
                coin_flips = np.random.random(len(self.data_feed))
                mask = coin_flips < self.sample_probability
                buffer = np.copy(valid_slice[mask])
            self.data_feed.index = 0
            self.data_source.dispatch(buffer)

    def event_loop(self):
        super(NumpySubscription, self).event_loop()


if __name__ == '__main__':
    unittest.main()
