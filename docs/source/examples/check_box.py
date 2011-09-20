#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from cStringIO import StringIO

from enaml.factory import EnamlFactory

enml = """
Window:
    title = "CheckBox example"
    Panel:
        VGroup:
            CheckBox:
                text = "I am a CheckBox"
                checked = True
            CheckBox:
                text = "I am another CheckBox"
"""

fact = EnamlFactory(StringIO(enml))

view = fact()

view.show()


