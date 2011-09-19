#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
""" A working example that tracks the development of the widgets
on the pyside branch and can be executed via python working_pyside_test.py 
from the current directory.

"""
from cStringIO import StringIO

from enaml.factory import EnamlFactory

enml = """
from datetime import date
Window:

    Panel:
        VGroup:
            CheckBox:
                toggled >> print(self.checked)
                pressed >> print('press')
                released >> print('release')
"""

fact = EnamlFactory(StringIO(enml))

view = fact()

view.show()


