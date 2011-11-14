#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import wx
from .wx_test_assistant import WXTestAssistant
from .. import group_box
from pdb import set_trace

class TestGroupBox(WXTestAssistant, group_box.TestGroupBox):

    def setUp(self):
        """ Setup for GroupBox testcases.

        1. Run the parent setup.
        2. Resize the widget and process events to allow for the private
           widgets to resize.

        """
        super(TestGroupBox, self).setUp()
        window = self.component_by_name(self.view, 'win')
        abstract = window.abstract_obj
        abstract.resize(200, 200)
        self.process_wx_events(self.app)

    def get_title(self, component, widget):
        """ Returns the title text from the tookit widget

        """
        self.process_wx_events(self.app)
        abstract = component.abstract_obj
        label = abstract._label
        return label.GetLabel()

    def get_flat(self, component, widget):
        """ Returns the flat style status from the tookit widget

        """
        self.process_wx_events(self.app)
        abstract = component.abstract_obj
        line = abstract._line
        border = abstract._border
        if line.IsShown():
            self.assertFalse(border.IsShown(), "The line and border widgets "
                "should not be shown at the same time")
            flat = True
        else:
            self.assertFalse(line.IsShown(), "The line and border widgets "
                "should not be hidden at the same time")
            flat = False
        return flat

    def get_title_align(self, component, widget):
        """ Returns the title aligment in the tookit widget

        """
        self.process_wx_events(self.app)
        # FIXME: this check depends on the size of the current window and
        # is not very reliable.
        abstract = component.abstract_obj
        title = abstract._label
        width, _ = widget.GetSizeTuple()
        title_rect = title.GetRect()
        result = []
        left_space = title_rect.Left
        right_space = width - title_rect.Right
        difference = (right_space - left_space)
        if -5 <= difference <= 5:
            result.append('center')
        if difference > 5:
            result.append('left')
        if difference < -5:
            result.append('right')
        self.assertTrue(len(result) == 1, "The position of the title "
                    "cannot be estimated reliably please increase the "
                    "resulting width of the Window")
        return result[0]
