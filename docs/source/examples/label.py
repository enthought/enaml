#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from cStringIO import StringIO

from enaml.factory import EnamlFactory

enml = """
Window:
    title = "Label example"
    Panel:
        HGroup:
            Label:
                text = "First label"
            Label:
                text = "Second label"
"""

fact = EnamlFactory(StringIO(enml))

view = fact()

view.show()
