#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from casuarius import ConstraintVariable 

from .qt.QtCore import QRect
from .qt_widget_component import QtWidgetComponent


class LayoutBox(object):
    """ A class which encapsulates a layout box using casuarius 
    constraint variables for the 'left', 'top', 'width', and 'height'
    primitives.

    """
    def __init__(self, name, owner_id):
        """ Initialize a LayoutBox.

        Parameters
        ----------
        name : str
            A name to use in the label for the constraint variables in
            this layout box.

        owner_id : str
            The owner id to use in the label for the constraint variables
            in this layout box.

        info : dict
            A layout info dictionary from Enaml which will be used to
            initialize this layout box.

        """
        label = '{0}_{1}'.format(name, owner_id)
        for primitive in ('left', 'top', 'width', 'height'):
            var = ConstraintVariable('{0}_{1}'.format(primitive, label))
            setattr(self, primitive, var)


class QtConstraintsWidget(QtWidgetComponent):
    """ A Qt4 implementation of an Enaml ConstraintsWidget.

    """
    #: A class attribte which indicates whether or not to use a 
    #: QWidgetItem to compute the layout geometry. Subclasses should
    #: override as necessary to change the behavior. 
    use_widget_item_for_layout = True

    #--------------------------------------------------------------------------
    # Initialization
    #--------------------------------------------------------------------------
    def initialize(self, init_attrs):
        """ Initialize the attributes of the widget.

        """
        super(QtConstraintsWidget, self).initialize(init_attrs)
        self.constraints_id = init_attrs['constraints_id']
        layout = init_attrs['layout']
        self.hug = layout['hug']
        self.resist_clip = layout['resist_clip']
        self.constraints = layout['constraints']

    #--------------------------------------------------------------------------
    # Properties
    #--------------------------------------------------------------------------
    @property
    def layout_box(self):
        """ A read-only cached property which creates the layout box
        for this object the first time it is requested.

        """
        try:
            res = self.__layout_box
        except AttributeError:
            name = type(self).__name__
            res = LayoutBox(name, self.constraints_id)
            self.__layout_box = res
        return res

    #--------------------------------------------------------------------------
    # Message Handlers
    #--------------------------------------------------------------------------
    def receive_relayout(self, ctxt):
        """ Handle the 'relayout' message from the Enaml widget.

        """
        print 'relayout!'

    #--------------------------------------------------------------------------
    # Layout Handling
    #--------------------------------------------------------------------------
    def size_hint_constraints(self):
        """ Creates the list of size hint constraints for this widget.

        This method using the provided size hint of the widget and the
        policies for 'hug' and 'resist_clip' to generate casuarius 
        LinearConstraint objects which respect the size hinting of the
        widget.

        If the size hint of the underlying widget is not valid, then
        no constraints will be generated.

        Returns
        -------
        result : list
            A list of casuarius LinearConstraint instances.

        """
        cns = []
        push = cns.append
        hint = self.layout_size_hint()
        if hint.isValid():
            width_hint = hint.width()
            height_hint = hint.height()
            box = self.layout_box
            width = box.width
            height = box.height
            hug_width, hug_height = self.hug
            resist_width, resist_height = self.resist_clip
            if width_hint >= 0:
                if hug_width != 'ignore':
                    cn = (width == width_hint) | hug_width
                    push(cn)
                if resist_width != 'ignore':
                    cn = (width >= width_hint) | resist_width
                    push(cn)
            if height_hint >= 0:
                if hug_height != 'ignore':
                    cn = (height == height_hint) | hug_height
                    push(cn)
                if resist_height != 'ignore':
                    cn = (height >= height_hint) | resist_height
                    push(cn)
        return cns

    def update_layout_geometry(self, dx, dy):
        """ A method which can be called during a layout pass to compute
        the new layout geometry rect and update the underlying widget.

        Parameters
        ----------
        dx : int
            The offset of the parent widget from the computed origin
            of the layout. This amount should be subtracted from the 
            computed layout 'x' amount.

        dy : int
            The offset of the parent widget from the computed origin
            of the layout. This amount should be subtracted from the
            computed layout 'y' amount.

        Returns
        -------
        result : (x, y)
            The computed layout 'x' and 'y' amount, unadjusted with
            the given dx and dy.

        """
        box = self.layout_box
        x = int(round(box.left.value))
        y = int(round(box.top.value))
        width = int(round(box.width.value))
        height = int(round(box.height.value))
        self.set_layout_geometry(x - dx, y - dy, width, height)
        return (x, y)

    def layout_size_hint(self):
        """ Returns the size hint to use in layout computation.

        The default implementation returns the appropriate size hint 
        based on whether or not a widget item should be used. If a
        subclass requires more control, it should override this method.

        Returns
        -------
        result : QSize
            The size hint to use in layout computations for the widget.

        """
        if self.use_widget_item_for_layout:
            item = self.widget_item
        else:
            item = self.widget
        size = item.sizeHint()
        return size

    def set_layout_geometry(self, x, y, width, height):
        """ Updates the layout geometry for the widget.

        The default implementation sets the geometry appropriately based
        on whether or not a widget item should be used. If a subclass
        requires more control, it should override this method.

        Parameters
        ----------
        x : int
            The x position of the widget, relative to the origin of
            its parent.

        y : int
            The y position of the widget, relative to the origin of
            its parent.

        width : int
            The width of the widget.

        height : int
            The height of the widget.

        """
        if self.use_widget_item_for_layout:
            item = self.widget_item
        else:
            item = self.widget
        item.setGeometry(QRect(x, y, width, height))

