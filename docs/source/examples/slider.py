#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from cStringIO import StringIO

from enaml.factory import EnamlFactory

enml = """
from enaml.enums import TickPosition

Window:
    title = "Slider example"
    Panel:
        HGroup:
            Slider:
                value = 0.5
                tick_interval = 0.05
                tick_position = TickPosition.BOTTOM
"""

fact = EnamlFactory(StringIO(enml))

view = fact()

view.show()
