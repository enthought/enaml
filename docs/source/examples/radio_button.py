#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from cStringIO import StringIO

from enaml.factory import EnamlFactory

enml = """
Window:
    title = "Radio button example"
    Panel:
        HGroup:
            RadioButton:
                style.cls = "stretch"
                text = 'rb1'
            RadioButton:
                style.cls = "stretch"
                text = 'rb2'
            RadioButton:
                style.cls = "stretch"
                text = 'rb3'
            RadioButton:
                style.cls = "stretch"
                text = 'rb4'
"""

fact = EnamlFactory(StringIO(enml))

view = fact()

view.show()
