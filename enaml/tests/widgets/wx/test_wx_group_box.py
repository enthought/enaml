#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import wx

from .wx_test_assistant import WXTestAssistant, skip_nonwindows

from .. import group_box


@skip_nonwindows
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
        return abstract.widget.GetTitle()

    def get_flat(self, component, widget):
        """ Returns the flat style status from the tookit widget

        """
        self.process_wx_events(self.app)
        abstract = component.abstract_obj
        return abstract.widget.GetFlat()

    def get_title_align(self, component, widget):
        """ Returns the title aligment in the tookit widget

        """
        self.process_wx_events(self.app)
        # FIXME: this check depends on the size of the current window and
        # is not very reliable.
        abstract = component.abstract_obj
        align = abstract.widget.GetAlignment()
        if align == wx.ALIGN_LEFT:
            res = 'left'
        elif align == wx.ALIGN_CENTER:
            res = 'center'
        elif align == wx.ALIGN_RIGHT:
            res = 'right'
        else:
            res = 'undefined'
        return res

