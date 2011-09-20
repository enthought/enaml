#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from cStringIO import StringIO

from enaml.factory import EnamlFactory

enml = """
Window:
    title = "HGroup example"
    Panel:
        HGroup:
            PushButton:
                style.cls = "stretch"
                text = 'rb1'
            PushButton:
                style.cls = "stretch"
                text = 'rb2'
            PushButton:
                style.cls = "stretch"
                text = 'rb3'
            PushButton:
                style.cls = "stretch"
                text = 'rb4'
"""

fact = EnamlFactory(StringIO(enml))

view = fact()

view.show()
