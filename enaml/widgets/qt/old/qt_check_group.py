#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from math import ceil

from .qt import QtGui

from traits.api import implements, List, Instance

from .qt_control import QtControl

from ..check_group import ICheckGroupImpl


class QtCheckGroup(QtControl):

    implements(ICheckGroupImpl)
    
    boxes = List(Instance(QtGui.QCheckBox))

    layout = Instance(QtGui.QGridLayout)

    #---------------------------------------------------------------------------
    # ICheckGroupImpl interface
    #---------------------------------------------------------------------------
    def create_widget(self):
        self.widget = QtGui.QFrame(self.parent_widget())
        
    def initialize_widget(self):
        self.layout = QtGui.QGridLayout()
        self.create_boxes()
        self.set_box_labels(self.parent.to_string)
        self.set_checked_state(self.parent.selected)

        # We want to layout the boxes after we set the checked state
        # since the state change may trigger a layout change that
        # would be otherwise lost.
        self.layout_boxes()
        self.widget.setLayout(self.layout)

    def parent_rows_changed(self, rows):
        """ Called when the number of rows changes. Will relayout the
        group according the to the number of rows.

        """
        self.clear_layout()
        self.layout_boxes()

    def parent_columns_changed(self, columns):
        """ Called when the number of columns changes. Will relayout the
        group according to the number of columns

        """
        self.clear_layout()
        self.layout_boxes()
        
    def parent_items_changed(self, items):
        """ Called when the list of items changes. Will relayout the 
        group according to the new items.

        """
        self.clear_layout()
        self.delete_boxes()
        self.initialize_widget()

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

    #---------------------------------------------------------------------------
    # Implementation
    #---------------------------------------------------------------------------
    def on_toggled(self, state):
        """ The toggle event handler for the check boxes. Updates the
        list of selected items when the check boxes are toggled.

        """
        res = []
        for item, box in zip(self.parent.items, self.boxes):
            if box.isChecked():
                res.append(item)
        self.parent.selected = res
    
    def set_box_labels(self, to_string):
        """ Sets the labels on the boxes with the provide conversion
        function.

        """
        items = self.parent.items
        boxes = self.boxes
        for item, box in zip(items, boxes):
            box.setText(to_string(item))

    def set_checked_state(self, selected):
        """ Sets the checked state of the boxes for the provided list
        of selected boxes.

        """
        boxes = self.boxes
        items = self.parent.items
        for item, box in zip(items, boxes):
            box.setChecked(item in selected)

    def create_boxes(self):
        """ Create checkbox widgets.

        """
        boxes = []
        box_parent = self.widget
        for item in self.parent.items:
            check_box = QtGui.QCheckBox(box_parent)
            check_box.toggled.connect(self.on_toggled)
            boxes.append(check_box)
        self.boxes = boxes
        
    def layout_boxes(self):
        """ Lay out the checkboxes in a grid. Num rows gets priority.

        """
        rows = self.parent.rows
        columns = self.parent.columns
        boxes = self.boxes

        nboxes = len(boxes)
        if rows > 0:
            columns = int(ceil(nboxes / float(rows)))
        elif columns > 0:
            pass
        else:
            columns = nboxes
             
        boxes = list(reversed(boxes))
        grid = []
        while boxes:
            row = []
            grid.append(row)
            for i in range(columns):
                try:
                    row.append(boxes.pop())
                except IndexError:
                    break
        
        layout = self.layout
        for i, cols in enumerate(grid):
            for j, check_box in enumerate(cols):
                layout.addWidget(check_box, i, j)
                
        layout.update()

    def clear_layout(self):
        """ Remove all the boxes from the layout.

        """
        for box in self.boxes:
            self.layout.removeWidget(box)

    def delete_boxes(self):
        """ Remove all of the boxes from the layout.

        """
        for box in self.boxes:
            self.widget.removeChild(box)
        self.boxes = []
        