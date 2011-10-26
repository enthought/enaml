#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt import QtCore, QtGui
from .qt_base_component import QtBaseComponent

from ..component import AbstractTkComponent

class QResizingFrame(QtGui.QFrame):
    """ A QFrame subclass that converts a resize event into a signal
    that can be connected to a slot. This allows the widget to notify
    Enaml that it has been resized and the layout needs to be recomputed.

    """
    resized = QtCore.Signal()

    def resizeEvent(self, event):
        self.resized.emit()


class QtComponent(QtBaseComponent, AbstractTkComponent):
    """ A Qt4 implementation of Component.

    A QtComponent is not meant to be used directly. It provides some 
    common functionality that is useful to all widgets and should 
    serve as the base class for all other classes. Note that this 
    is not a HasTraits class.

    """
    #: The Qt widget created by the component
    widget = None

    #--------------------------------------------------------------------------
    # Setup Methods
    #--------------------------------------------------------------------------
    def create(self):
        self.widget = QResizingFrame(self.parent_widget())
    
    def bind(self):
        super(QtComponent, self).bind()
        
        # This is a hack at the moment
        if hasattr(self.widget, 'resized'):
            self.widget.resized.connect(self.on_resize)

    #--------------------------------------------------------------------------
    # Implementation
    #--------------------------------------------------------------------------
    @property
    def toolkit_widget(self):
        """ A property that returns the toolkit specific widget for this
        component.

        """
        return self.widget
    
    def size(self):
        """ Return the size of the internal toolkit widget as a 
        (width, height) tuple of integers.

        """
        widget = self.widget
        return (widget.width(), widget.height())
    
    def size_hint(self):
        """ Returns a (width, height) tuple of integers which represent
        the suggested size of the widget for its current state. This 
        value is used by the layout manager to determine how much 
        space to allocate the widget.

        """
        size_hint = self.widget.sizeHint()
        return (size_hint.width(), size_hint.height())

    def resize(self, width, height):
        """ Resizes the internal toolkit widget according the given
        width and height integers.

        """
        self.widget.resize(width, height)
    
    def pos(self):
        """ Returns the position of the internal toolkit widget as an 
        (x, y) tuple of integers. The coordinates should be relative to
        the origin of the widget's parent.

        """
        widget = self.widget
        return (widget.x(), widget.y())
    
    def move(self, x, y):
        """ Moves the internal toolkit widget according to the given
        x and y integers which are relative to the origin of the
        widget's parent.

        """
        self.widget.move(x, y)
    
    def geometry(self):
        """ Returns an (x, y, width, height) tuple of geometry info
        for the internal toolkit widget. The semantic meaning of the
        values are the same as for the 'size' and 'pos' methods.

        """
        x, y = self.pos()
        width, height = self.size()
        return (x, y, width, height)
    
    def set_geometry(self, x, y, width, height):
        """ Sets the geometry of the internal widget to the given 
        x, y, width, and height values. The semantic meaning of the
        values is the same as for the 'resize' and 'move' methods.

        """
        self.widget.setGeometry(x, y, width, height)
    
    def on_resize(self):
        # should handle the widget resizing by telling something
        # that things need to be relayed out
        pass

    #--------------------------------------------------------------------------
    # Convienence methods
    #--------------------------------------------------------------------------
    def parent_widget(self):
        """ Returns the logical QWidget parent for this component. 

        Since some parents may wrap non-Widget objects, this method will
        walk up the tree of components until a QWidget is found or None 
        if no QWidget is found.

        Returns
        -------
        result : QWidget or None

        """
        # XXX do we need to do this still? i.e. can we now have a parent
        # that doesn't create a widget???
        shell_parent = self.shell_obj.parent
        while shell_parent:
            widget = shell_parent.toolkit_widget
            if isinstance(widget, QtGui.QWidget):
                return widget
            shell_parent = shell_parent.parent
        
    def child_widgets(self):
        """ Iterates over the shell widget's children and yields the 
        toolkit widgets for those children.

        """
        for child in self.shell_obj.children:
            yield child.toolkit_widget

