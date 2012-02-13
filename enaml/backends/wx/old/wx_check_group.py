#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import math

import wx

from traits.api import implements, List, Instance

from .wx_control import WXControl

from ..check_group import ICheckGroupImpl


class WXCheckGroup(WXControl):

    implements(ICheckGroupImpl)

    boxes = List(Instance(wx.CheckBox))

    sizer = Instance(wx.GridSizer)

    #---------------------------------------------------------------------------
    # ICheckGroupImpl interface
    #---------------------------------------------------------------------------
    def create_widget(self):
        self.widget = wx.Panel(self.parent_widget())

    def initialize_widget(self):
        self.create_boxes()
        self.set_box_labels(self.parent.to_string)
        self.set_checked_state(self.parent.selected)

        # We want to layout the boxes after we set the checked state
        # since the state change may trigger a layout change that
        # would be otherwise lost.
        self.layout_boxes()
        self.widget.SetSizer(self.sizer)

    def shell_rows_changed(self, rows):
        """ Called when the number of rows changes. Will relayout the
        group according the to the number of rows.

        """
        self.destroy_boxes()
        self.initialize_widget()
        self.widget.GetParent().Layout()

    def shell_columns_changed(self, columns):
        """ Called when the number of columns changes. Will relayout the
        group according to the number of columns

        """
        self.destroy_boxes()
        self.initialize_widget()
        self.widget.GetParent().Layout()

    def shell_items_changed(self, items):
        """ Called when the list of items changes. Will relayout the
        group according to the new items.

        """
        self.destroy_boxes()
        self.initialize_widget()
        self.widget.GetParent().Layout()

    def shell_selected_changed(self, selected):
        """ Called when the list of selected items changes. Will set
        the checked state of the appropriate check boxes.

        """
        self.set_checked_state(selected)

    def shell_to_string_changed(self, to_string):
        """ Called when the to_string function changes. Will relabel
        the boxes according to the new coversion function.

        """
        self.set_box_labels(to_string)
        self.widget.GetParent().Layout()

    #---------------------------------------------------------------------------
    # Implementation
    #---------------------------------------------------------------------------
    def create_boxes(self):
        """ Creates the list of check boxes for the group.

        """
        boxes = []
        box_parent = self.widget
        for item in self.parent.items:
            check_box = wx.CheckBox(box_parent)
            check_box.Bind(wx.EVT_CHECKBOX, self.on_toggled)
            boxes.append(check_box)
        self.boxes = boxes

    def destroy_boxes(self):
        """ Destroys all of the check boxes in the group.

        """
        for box in self.boxes:
            box.Destroy()
        self.boxes = []

    def layout_boxes(self):
        """ Lays out the check boxes in an appropriate grid.

        """
        # XXX wx still manages to bork this up when the row count
        # dynamically changes to 1. On Windows, it results in all of
        # the check boxes being drawn on top of one another. Explicitly
        # setting the row and columns sizes doesn't help. I'm adding
        # this to my long list of reasons I hate wx.
        sizer = wx.GridSizer()
        rows = self.parent.rows
        columns = self.parent.columns
        nitems = len(self.parent.items)

        if rows > 0:
            sizer.SetRows(rows)
        elif columns > 0:
            rows = math.ceil(nitems / columns)
            sizer.SetRows(rows)
        else:
            sizer.SetRows(1)

        for box in self.boxes:
            sizer.Add(box, 1)

        sizer.Layout()
        self.sizer = sizer

    def on_toggled(self, event):
        """ The toggle event handler for the check boxes. Updates the
        list of selected items when the check boxes are toggled.

        """
        res = []
        for item, box in zip(self.parent.items, self.boxes):
            if box.GetValue():
                res.append(item)
        self.parent.selected = res

    def set_box_labels(self, to_string):
        """ Sets the labels on the boxes with the provide conversion
        function.

        """
        items = self.parent.items
        boxes = self.boxes
        for item, box in zip(items, boxes):
            box.SetLabel(to_string(item))

    def set_checked_state(self, selected):
        """ Sets the checked state of the boxes for the provided list
        of selected boxes.

        """
        boxes = self.boxes
        items = self.parent.items
        for item, box in zip(items, boxes):
            if item in selected:
                box.SetValue(True)

