#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from cStringIO import StringIO

from enaml.factory import EnamlFactory

enml = """
Window:
    title = "Form example"
    Panel:
        Form:
            Field:
                name = 'Name'
            Field:
                name = 'Surname'
"""

fact = EnamlFactory(StringIO(enml))

view = fact()

view.show()
