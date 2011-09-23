#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
#!/usr/bin/env python
import unittest

class EnamlTestCase(unittest.TestCase):
    """ Testsuite class for enaml widgets

    To test the enaml widgets subclass and add the enaml source code
    to the enaml_source attribute ans in the example::

        class testWXLabel(EnamlTestCase):

        enaml_source = \
        '''
        Window:
            Panel:
                VGroup:
                    Label:
                        name = 'tested_widget'
                        text = 'test label'
        '''

        ... <testing code> ...


    Currently the test suite allows to interact with the enaml widgets
    in a gui application without the event loop running. The enaml widget
    can be easily accessed using the get_widget function and providing the
    name of the desired widget.

    .. note:: If you need to change the setUp and tearDown functions you
        need to call the baseclass versions so the widget is initialized
        properly

    """

    #: enaml mutli-string source to use for creating the widgets
    enaml_source = None

    def setUp(self):
        from cStringIO import StringIO
        from enaml.factory import EnamlFactory
        fact = EnamlFactory(StringIO(self.enaml))
        view = fact()
        if not view._style_sheet_applied:
            view._apply_style_sheet()
        self.window = view.window
        self.window.show()

    def get_widget(self, widget_name, current=None):
        """ Parse the enaml widget hierarchy and return the widget with
        the given name.

        Use this
        """
        if current is None:
            current = self.window

        if current.name == widget_name:
            return current
        elif len(current.children):
            for child in current.children:
                widget = self.get_widget(widget_name, child)
                if widget is not None:
                    return widget

        return None


    def tearDown(self):
        self.window.hide()
        pass
