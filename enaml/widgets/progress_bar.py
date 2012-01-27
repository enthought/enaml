#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from abc import abstractmethod

from traits.api import Int, Instance, Property, TraitError, on_trait_change

from .control import Control, AbstractTkControl

from ..core.trait_types import Bounded


class AbstractTkProgressBar(AbstractTkControl):

    @abstractmethod
    def shell_value_changed(self, value):
        raise NotImplementedError

    @abstractmethod
    def shell_minimum_changed(self, minimum):
        raise NotImplementedError

    @abstractmethod
    def shell_maximum_changed(self, maximum):
        raise NotImplementedError


class ProgressBar(Control):
    """ A progress bar.

    """
    #: The minimum value that the progress bar can take. Extra checks
    #: take place to make sure that the user does not programmatically 
    #: set :attr:`minimum` > :attr:`maximum`.
    minimum = Property(Int, depends_on='_minimum')

    #: The internal min value storage
    _minimum = Int(0)

    #: The maximum value that the progress bar can take. Extra checks 
    #: take place to make sure that the user does not programmatically 
    #: set :attr:`minimum` > :attr:`maximum`.
    maximum = Property(Int, depends_on='_maximum')

    #: The internal max value storage
    _maximum = Int(100)

    #: The current value. Default is the minimum value. The value is 
    #: bounded between :attr:`minimum` and :attr:`maximum`. Changing 
    #: the boundary attributes might result in an update of :attr:`value` 
    #: to fit in the new range. Attempts to assign a value outside of 
    #: these bounds will result in a TraitError.
    value = Bounded(0, low='minimum', high='maximum')

    #: The percentage completed, rounded to an integer. This is a 
    #: readonly property for convenient use by other Components.
    percentage = Property(Int, depends_on=['_minimum', '_maximum', 'value'])

    #: How strongly a component hugs it's content. ProgressBars expand 
    #: to fill the available horizontal space by default.
    hug_width = 'ignore'

    #: Overridden parent class trait
    abstract_obj = Instance(AbstractTkProgressBar)

    #--------------------------------------------------------------------------
    # Property methods
    #--------------------------------------------------------------------------
    def _set_minimum(self, value):
        """ The property setter for :attr:`minimum`. Addtional checks are 
        applied to make sure that :attr:`minimum` < :attr:`maximum`

        """
        if value > self.maximum:
            msg = ('The minimum value of ProgressBar should be smaller than '
                   'the current maximum value({0}), but a value of {1} was '
                   'given')
            msg = msg.format(self.maximum, value)
            raise TraitError(msg)
        self._minimum = value

    def _set_maximum(self, value):
        """ The property setter for :attr:`maximum`. Addtional checks are 
        applied to make sure that :attr:`minimum` < :attr:`maximum`

        """
        if value < self.minimum:
            msg = ('The maximum value of ProgressBar should be larger than '
                   'the current minimum value({0}), but a value of {1} was '
                   'given')
            msg = msg.format(self.minimum, value)
            raise TraitError(msg)
        self._maximum = value

    def _get_maximum(self):
        """ The property getter for the ProgressBar maximum.

        """
        return self._maximum

    def _get_minimum(self):
        """ The property getter for the ProgressBar minimum.

        """
        return self._minimum

    def _get_percentage(self):
        """ The property getter for the ProgressBar percentage.

        """
        minimum = self.minimum
        maximum = self.maximum
        value = self.value
        dy = maximum - minimum
        if dy == 0:
            res = 0
        elif value == maximum:
            res = 100
        else:
            dx = float(value - minimum)
            res = int(round(100.0 * dx / dy))
            # We already excluded the case where the value was exactly the 
            # maximum, so we can't really be at 100%, so round this down to 
            # 99% if necessary.
            res = min(res, 99)
        return res

    @on_trait_change('minimum, maximum')
    def _adapt_value(self):
        """ Adapt the value to the boundaries

        """
        if self.initialized:
            self.value = min(max(self.value, self.minimum), self.maximum)

