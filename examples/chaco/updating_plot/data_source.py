#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
""" The DataSource api for providing live streaming data to a Chaco plot.

"""
from abc import ABCMeta, abstractmethod
from enaml.core.signaling import Signal
import numpy as np


class AbstractDataSource(object):
    """ An abstract base class which defines the interface for a data
    source to be used by a live plot.

    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def subscribe(self, callback):
        """ Subscribe a callback to be called by the data source when
        new data is available. The argument will be a structured numpy
        array representing all of the data. Only a weak reference is
        maintained to the callback.

        """
        raise NotImplementedError

    @abstractmethod
    def unsubscribe(self, callback):
        """ Unsubscribe a callback that was registered previously 
        via a call to subscribe.

        """
        raise NotImplementedError

    @abstractmethod
    def bind(self):
        """ Bind this data source to the publisher. The data source
        will start listening to the publisher immediately.

        """
        raise NotImplementedError


class DataSource(AbstractDataSource):
    """ A trival but concrete implementation of AbstractDataSource which 
    handles basic functionality for manipulation of incoming timestamp 
    data.

    """
    #: The signal object used to manage subscriptions
    _data_changed = Signal()

    def __init__(self, publisher, buffer_size=1000000, sampler=None):
        """ Initialize a TimeStampDataSource.

        Parameters
        ----------
        publisher : AbstractPublisher
            A publisher instance which is publishing the feed we're
            interested in, at the rate at which we need it.

        buffer_size : int, optional
            The size of the data buffer to maintain. A full buffer is
            implemented as a sliding window across the incoming data.
            The default buffer size is 1e6.
        
        sampler : AbstractDataSampler, optional
            If provided, an instance of AbstractDataSampler which has
            the opportunity to subsample the data before it is 
            republished to subcribers.

        """
        self.buffer_size = buffer_size
        self.sampler = sampler
        self.publisher = publisher
        self._buffer = None

    def dispatch(self, data):
        """ The publisher callback which aggregates the new data and 
        emits the _data_changed signal.

        """
        buf = self._buffer
        max_size = self.buffer_size
        if len(data) >= max_size:
            buf = np.copy(data[-max_size:])
        else:
            if buf is None:
                buf = np.copy(data)
            else:
                offset = max_size - len(data)
                buf = np.hstack((buf[-offset:], data))
        sampler = self.sampler
        if sampler is not None:
            buf = sampler(buf)

        self._buffer = buf
        self._data_changed(buf)

    def bind(self):
        """ Bind the data source to the given publisher. This may only
        happen once.

        """
        self.publisher.subscribe(self.dispatch)

    def subscribe(self, callback):
        """ Subscribe the given callback to be notified when new
        data is available.

        """
        self._data_changed.connect(callback)

    def unsubscribe(self, callback):
        """ Unsubscribe a previously registered callback.

        """
        self._data_changed.disconnect(callback)

