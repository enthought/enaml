#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from enaml import qt_toolkit


class QtTestAssistant(object):
    """ Assistant class for testing wx based components.

    This class is to be used as a mixing with the base enaml test case
    class for the components tests of the qt backend. It sets the correct
    toolkit attribute and (in the future) provide some useful methods for
    testin Qt based components.

    """

    toolkit = qt_toolkit()

