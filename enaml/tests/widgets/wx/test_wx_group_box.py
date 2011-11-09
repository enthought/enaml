#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .wx_test_assistant import WXTestAssistant
from .. import group_box

class TestGroupBox(WXTestAssistant, group_box.TestGroupBox):

    def setUp(self):
        """ Setup for GroupBox testcases.

        1. Run the parent setup.
        2. Resize the widget and process events to allow for the private
           widgets to resize.

        """
        super(TestGroupBox, self).setUp()
        widget = self.widget
        widget.SetSizeWH(200, 200)
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
        if left_space <= 10:
            result.append('left')
        if right_space <= 10:
            result.append('right')
        if -5 <= (right_space - left_space) <= 5:
            result.append('center')
        self.assertTrue(len(result) == 1, "The position of the title "
                    "cannot be estimated reliably please increase the "
                    "resulting width of the Window")
        return result[0]
