#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from cStringIO import StringIO

from enaml.factory import EnamlFactory

enml = """
from datetime import date
Window:
    title = "Calendar example"
    Panel:
        VGroup:
            Calendar:
                minimum_date = date(2012, 1, 1)
"""

fact = EnamlFactory(StringIO(enml))

view = fact()

view.show()


