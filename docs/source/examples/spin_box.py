#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from cStringIO import StringIO

from enaml.factory import EnamlFactory

enml = """
Window:
    title = "SpinBox example"
    Panel:
        VGroup:
            SpinBox:
                special_value_text = "Auto"
                step = 2
                low = -20
                high = 20
"""

fact = EnamlFactory(StringIO(enml))

view = fact()

view.show()
