import wx

from traits.api import implements, List, Instance

from .wx_control import WXControl

from ..check_group import ICheckGroupImpl


class WXCheckGroup(WXControl):

    implements(ICheckGroupImpl)
    
    boxes = List(Instance(wx.CheckBox))

    #---------------------------------------------------------------------------
    # ICheckGroupImpl interface
    #---------------------------------------------------------------------------
    def create_widget(self):
        self.widget = wx.Panel(self.parent_widget())
        
    def initialize_widget(self):
        sizer = wx.GridSizer(wx.HORIZONTAL)
        rows = self.parent.rows
        columns = self.parent.columns
        if rows > 0:
            sizer.SetRows(self.parent.rows)
        if columns > 0:
            sizer.SetCols(self.parent.columns)

        boxes = []
        box_parent = self.widget
        for item in self.parent.items:
            check_box = wx.CheckBox(box_parent)
            check_box.Bind(wx.EVT_CHECKBOX, self.on_toggled)
            boxes.append(check_box)
            sizer.Add(check_box, 1)
    
        self.boxes = boxes
        self.set_box_labels(self.parent.to_string)
        self.set_checked_state(self.parent.selected)
        self.widget.SetSizer(sizer)
        sizer.Layout()

    def parent_rows_changed(self, rows):
        """ Called when the number of rows changes. Will relayout the
        group according the to the number of rows.

        """
        for box in self.boxes:
            box.Destroy()
        self.initialize_widget()
        self.widget.GetParent().Layout()

    def parent_columns_changed(self, columns):
        """ Called when the number of columns changes. Will relayout the
        group according to the number of columns

        """
        for box in self.boxes:
            box.Destroy()
        self.initialize_widget()
        self.widget.GetParent().Layout()
        
    def parent_items_changed(self, items):
        """ Called when the list of items changes. Will relayout the 
        group according to the new items.

        """
        for box in self.boxes:
            box.Destroy()
        self.initialize_widget()
        self.widget.GetParent().Layout()

    def parent_selected_changed(self, selected):
        """ Called when the list of selected items changes. Will set
        the checked state of the appropriate check boxes.

        """
        self.set_checked_state(selected)

    def parent_to_string_changed(self, to_string):
        """ Called when the to_string function changes. Will relabel
        the boxes according to the new coversion function.

        """
        self.set_box_labels(to_string)
        self.widget.GetParent().Layout()

    #---------------------------------------------------------------------------
    # Implementation
    #---------------------------------------------------------------------------
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

