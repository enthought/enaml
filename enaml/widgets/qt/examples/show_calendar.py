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
            Calendar:
                minimum_date = date(2012, 1, 1)
                activated >> print('activated', self.date)
                selected >> print('selected', msg.new)
"""

fact = EnamlFactory(StringIO(enml))

view = fact()

view.show()


