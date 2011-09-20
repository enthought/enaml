#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from cStringIO import StringIO

from enaml.factory import EnamlFactory

enml = """
Window:
    title = "Push button example"
    Panel:
        HGroup:
            PushButton:
                text = "Press me"
            PushButton:
                text = "or Press me"
"""

fact = EnamlFactory(StringIO(enml))

view = fact()

view.show()
