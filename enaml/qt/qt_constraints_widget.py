#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from casuarius import ConstraintVariable 

from .qt.QtCore import QRect
from .qt_widget_component import QtWidgetComponent


class LayoutBox(object):
    """ A class which encapsulates a layout box using casuarius 
    constraint variables.

    The constraint variables are created on an as-needed basis, this
    allows Enaml widgets to define new constraints and build layouts
    with them, without having to specifically update this client 
    code.

    """
    def __init__(self, name, owner):
        """ Initialize a LayoutBox.

        Parameters
        ----------
        name : str
            A name to use in the label for the constraint variables in
            this layout box.

        owner : str
            The owner id to use in the label for the constraint variables
            in this layout box.

        """
        self._name = name
        self._owner = owner
        self._primitives = {}

    def primitive(self, name, force_create=True):
        """ Returns a primitive casuarius constraint variable for the
        given name.

        Parameters
        ----------
        name : str
            The name of the constraint variable to return.

        force_create : bool, optional
            If the constraint variable does not yet exist and this 
            parameter is True, then the constraint variable will be
            created on-the-fly. If the parameter is False, and the
            variable does not exist, a ValueError will be raised.

        """
        primitives = self._primitives
        try:
            res = primitives[name]
        except KeyError:
            if force_create:
                label = '{0}_{1}'.format(self._name, self._owner)
                res = primitives[name] = ConstraintVariable(label)
            else:
                msg = 'Constraint variable `{0}` does not exist'
                raise ValueError(msg.format(name))
        return res


class QtConstraintsWidget(QtWidgetComponent):
    """ A Qt implementation of an Enaml ConstraintsWidget.

    """
    #: A class attribte which indicates whether or not to use a 
    #: QWidgetItem to compute the layout geometry. Subclasses should
    #: override as necessary to change the behavior. 
    use_widget_item_for_layout = True

    #--------------------------------------------------------------------------
    # Setup Methods
    #--------------------------------------------------------------------------
    def create(self, tree):
        """ Create and initialize the underlyling widget.

        """
        super(QtConstraintsWidget, self).create(tree)
        layout = tree['layout']
        self.hug = layout['hug']
        self.resist_clip = layout['resist_clip']
        self.constraints = layout['constraints']
        self.layout_box = LayoutBox(type(self).__name__, self.widget_id())
        
    #--------------------------------------------------------------------------
    # Message Handlers
    #--------------------------------------------------------------------------
    def on_action_relayout(self, content):
        """ Handle the 'relayout' action from the Enaml widget.

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
            primitive = self.layout_box.primitive
            width = primitive('width')
            height = primitive('height')
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
            item = self.widget_item()
        else:
            item = self.widget()
        size = item.sizeHint()
        return size

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
        primitive = self.layout_box.primitive
        x = int(round(primitive('left', False).value))
        y = int(round(primitive('top', False).value))
        width = int(round(primitive('width', False).value))
        height = int(round(primitive('height', False).value))
        self.set_layout_geometry(x - dx, y - dy, width, height)
        return (x, y)
    
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
            item = self.widget_item()
        else:
            item = self.widget()
        item.setGeometry(QRect(x, y, width, height))

