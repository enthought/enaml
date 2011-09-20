#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from cStringIO import StringIO

from enaml.factory import EnamlFactory

enml = """
Window:
    title = "Field example"
    Panel:
        VGroup:
            Label:
                text = "This is an integer field"
            Field mf:
                to_string = str
                from_string = lambda val: int(val) if val else 0
                value = 0
                style.background_color << "error" if self.error else "nocolor"
"""

fact = EnamlFactory(StringIO(enml))

view = fact()

view.show()
