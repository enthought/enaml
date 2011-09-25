#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import unittest
from cStringIO import StringIO

from enaml.factory import EnamlFactory


class EnamlTestCase(object):
    """ Base class for testing Enaml widgets. """
    
    def setUp(self):
        """ Parse Enaml source, stored in `self.enaml`, and store the view. """
        
        events = []
        fact = EnamlFactory(StringIO(self.enaml))
        view = fact(events=events)
        
        # Lay widgets out, but don't display them to screen.
        view._apply_style_sheet()
        view.window.layout()
        
        self.namespace = view.ns
        self.view = view
        self.events = events
    
    def widget_by_id(self, widget_id):
        """ Find an item in the view's namespace with a given id.
        
        Raises
        ------
        AttributeError if no such name exists.

        """
        return getattr(self.namespace, widget_id)
        
