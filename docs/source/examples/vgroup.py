#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from cStringIO import StringIO

from enaml.factory import EnamlFactory

enml = """
Window:
    title = "VGroup example"
    Panel:
        VGroup:
            PushButton:
                style.cls = "stretch"
                text = 'b1'
            PushButton:
                style.cls = "stretch"
                text = 'b2'
            PushButton:
                style.cls = "stretch"
                text = 'b3'
            PushButton:
                style.cls = "stretch"
                text = 'b4'
"""

fact = EnamlFactory(StringIO(enml))

view = fact()

view.show()
