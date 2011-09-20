#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from cStringIO import StringIO

from enaml.factory import EnamlFactory

enml = """
Window:
    title = "Html example"
    Panel:
        VGroup:
            Html:
                source = (
                          "<p><b>This text is bold</b></p>"
                          "<p><i>This text is italic</i></p>"
                          "<p><small>This text is small</small></p>"
                          "<p>This is<sub> subscript</sub> and <sup>superscript</sup></p>"
                          )
"""

fact = EnamlFactory(StringIO(enml))

view = fact()

view.show()
