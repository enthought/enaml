#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
""" A fake data generated which can generate data at various frequencies.
This is not intended for production use, but rather as a stand-in for
some external data generation feed.

"""
from abc import ABCMeta, abstractmethod
from collections import defaultdict
import threading
import time


class AbstractDataGenerator(object):
    """ An abstract base class which defines the dummy api for a 
    data generator.

    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def subscribe(self, id, callback):
        """ Register a callback to be called when data is available
        for the given id.
        
        """
        raise NotImplementedError
        
 
class DummyDataGenerator(object):
    """ A dummy data generator which generates timestamp data on a
    specified frequency.

    This class is for demonstration purposes only, and will be 
    replaced with an actualy production data source.

    """
    def __init__(self, frequency, *value_gens):
        """ Initialize a DummyDataGenerator

        Parameters
        ----------
        frequencey : float
            A floating point frequency (Hz) which indicates how
            freqeuntly data should be generated.
        
        *value_gens : callables
            Callables which are called with the time stamp and return
            a tuple of (id, value) where id is a string representing
            the feed id and value is the datapoint for the time stamp.
            These values will be republished to any listeners.

        """
        self.callback = None
        self.go = True
        self.frequency = frequency
        self.callbacks = defaultdict(list)
        self.value_gens = value_gens

    def start(self):
        """ Start the generator's generation thread. Any registered
        callbacks will be called when new data is available.

        """
        def inner(data_generator):
            while(data_generator.go):
                time_stamp =  time.clock()
                callbacks = data_generator.callbacks
                for gen in data_generator.value_gens:
                    id, data = gen(time_stamp)
                    for cb in callbacks[id]:
                        cb((id, time_stamp, data))
                time.sleep(1.0 / data_generator.frequency)
        thread = threading.Thread(target=inner, args=(self,))
        thread.daemon = True
        thread.start()

    def stop(self):
        """ Stop the generator's generation thread.

        """
        self.go = False

    def subscribe(self, id, callback):
        """ Register a callback to be called when data is available
        for the given id.
        
        """
        self.callbacks[id].append(callback)

