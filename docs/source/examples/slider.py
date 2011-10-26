#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from cStringIO import StringIO

from enaml.factory import EnamlFactory

enml = """
Window:
    title = "Slider example"
    Panel:
        HGroup:
            Slider:
                value = 0.5
                tick_interval = 0.05
                tick_position = 'bottom'
"""

fact = EnamlFactory(StringIO(enml))

view = fact()

view.show()
