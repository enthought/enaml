#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
""" A data sampler api for subsampling a data stream.

"""
from abc import ABCMeta, abstractmethod
import numpy as np


class AbstractDataSampler(object):
    """ An abstract base class which defines the api necessary for a
    data sampler.

    """
    __metaclass__ = ABCMeta
    @abstractmethod
    def sample(self, data):
        """ Samples the given data buffer and returns a possibly new
        buffer with subsampled data.

        Parameters
        ----------
        data : np.ndarray
            The buffer of data to be sampled.
        
        Returns
        -------
        result : np.ndarray
            A new buffer of sampled data, or the original buffer if 
            no sampling needs to be performed.

        """
        raise NotImplementedError


class ProbabilitySampler(AbstractDataSampler):
    """ A concrete implementation of AbstractDataSampler which sub 
    samples data based on a uniform probability distribution.

    """
    def __init__(self, probability=1.0):
        """ Initialized a ProbabilitySampler.

        Parameters
        ----------
        probability : float, optional
            A floating point probability in the range(0.0, 1.0)
        
        """
        prob = probability
        assert 0.0 <= prob <= 1.0, "Probability must be 0.0 <= val <= 1.0"
        self.probability = prob 

    def sample(self, data):
        num_entries = data.shape[0]
        coin_flips = np.random.random(num_entries)
        mask = coin_flips < self.probability
        return data[mask]

