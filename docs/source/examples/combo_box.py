#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from cStringIO import StringIO

from enaml.factory import EnamlFactory

enml = """
Window:
    title = "ComboBox example"
    Panel:
        VGroup:
            ComboBox:
                items = ['first choice', 'second choice']
                value = 'first choice'
"""

fact = EnamlFactory(StringIO(enml))

view = fact()

view.show()


