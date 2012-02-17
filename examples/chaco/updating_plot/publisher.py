#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
""" A simple publisher api that acts as a throttling broadcaster for a 
high frequency data source.

"""
import threading
import time
from abc import ABCMeta, abstractmethod
import numpy as np
from enaml.core.signaling import Signal


TIMESTAMP_FLOAT32_DTYPE = np.dtype(
    [('index', np.float64), ('value', np.float32)]
)


class AbstractPublisher(object):
    """ An abstract base class representing a data republisher. A 
    publisher subcsribes to a given feed id but throttles updates 
    to a rate which is manageable for the given task.

    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def start(self):
        """ Start the publisher feed.

        """
        raise NotImplementedError

    @abstractmethod
    def stop(self):
        """ Stop the publisher feed.

        """
        raise NotImplementedError

    @abstractmethod
    def subscribe(self, callback):
        """ Subscribe a callback to the feed which will be called with
        a structured numpy array when data is available.

        """
        raise NotImplementedError

    @abstractmethod
    def unsubscribe(self, callback):
        """ Unsubscribe a callback previously registered via subscribe.

        """
        raise NotImplementedError


class BasePublisher(AbstractPublisher):
    """ A base publisher class which provides a simple event loop for
    processing a feed.

    """
    #: The signal used to implement notification
    _data_changed = Signal()

    #: The default event loop frequency
    frequency = 30

    def start_event_loop(self):
        """ A simple event loop implemented with a daemon thread.

        """
        def inner(publisher):
            while publisher._go_thread:
                buf = publisher.process_feed()
                publisher._data_changed(buf)
                time.sleep(1.0 / publisher.frequency)
        self._go_thread = True
        thread = threading.Thread(target=inner, args=(self,))
        thread.daemon = True
        thread.start()
    
    def stop_event_loop(self):
        """ Stop the event loop thread.

        """
        self._go_thread = False
    
    def subscribe(self, callback):
        """ Subscribe a callback to the publisher. Callbacks will be
        notified from a thread.

        """
        self._data_changed.connect(callback)

    def unsubscribe(self, callback):
        """ Unsubscribe a previously registered callback.

        """
        self._data_changed.disconnect(callback)

    @abstractmethod
    def process_feed(self):
        """ Do any necessary processing on the queued feed and return
        the value to be emitted to any listeners. This method will be 
        called from a thread.

        """
        raise NotImplementedError


class NumpyPublisher(BasePublisher):
    """ A concrete implementation of BasePublisher which acummulates the
    data into a numpy array.

    """

    def __init__(self, data_gen, id, size=1000000, frequency=30, sampler=None):
        """ Initialize a NumpyPublisher.

        Parameters
        ----------
        data_gen : AbstractDataGenerator
            An AbstractDataGenerator instance which provides the feeds
            we are interested in.
        
        id : string
            The identifier for the particular data feed from the data
            generator which should be republished to any subscribers.
        
        size : int, optional
            The size of the buffer to queue incoming data. The default
            is 1e6.
        
        frequency : int, optional
            The frequency with which to republish data. The default
            is 30 (Hz)
        
        sampler : AbstractDataSampler, optional
            If provided, an instance of AbstractDataSampler which has
            the opportunity to subsample the data before it is 
            republished to subcribers.
        
        """
        self.data_gen = data_gen
        self.feed_id = id
        self.frequency = frequency
        self.sampler = sampler
        self._buffer = np.empty(size, dtype=TIMESTAMP_FLOAT32_DTYPE)
        self.size = size
        self.index = 0
        self.lock = threading.Lock()
    
    #--------------------------------------------------------------------------
    # AbstractPublisher Implementation
    #--------------------------------------------------------------------------
    def start(self):
        """ Bind to the data feed with the given id and start the 
        event loop.

        """
        self.data_gen.subscribe(self.feed_id, self.insert)
        self.start_event_loop()

    def stop(self):
        """ Stop the publisher feed.

        """
        self.stop_event_loop()

    def process_feed(self):
        """ Process and return the current buffered data.

        """
        with self.lock:
            data = np.copy(self._buffer[:self.index])
        sampler = self.sampler
        if sampler is not None:
            data = sampler.sample(data)
        self.index = 0
        return data

    #--------------------------------------------------------------------------
    # Processing Helpers
    #--------------------------------------------------------------------------    
    def insert(self, value):
        """ The callback from the data feed which inserts the data point
        into the internal buffer.

        """
        with self.lock:
            if self.index >= self.size:
                raise BufferError
            id, idx, val = value
            item = self._buffer[self.index]
            item['index'] = idx
            item['value'] = val
            self.index += 1
            
