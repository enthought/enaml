#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt import QtCore, QtGui

from traits.api import implements, HasStrictTraits, WeakRef, Instance

from ..component import Component, IComponentImpl

class QtComponent(HasStrictTraits):
    """ A Qt4 implementation of Component.

    A QtComponent is not meant to be used directly. It provides some 
    common functionality that is useful to all widgets and should 
    serve as the base class for all other classes.

    See Also
    --------
    Component

    """
    implements(IComponentImpl)

    #---------------------------------------------------------------------------
    # IComponentImpl interface
    #---------------------------------------------------------------------------
    parent = WeakRef(Component)

    def set_parent(self, parent):
        """ Sets the parent component to the given parent.

        """
        self.parent = parent
        
    def create_widget(self):
        """ Creates the underlying wx widget. Must be implemented by 
        subclasses.

        """
        raise NotImplementedError
    
    def initialize_widget(self):
        """ Initializes the attribtues of a wiget. Must be implemented
        by subclasses.

        """
        raise NotImplementedError
    
    def create_style_handler(self):
        """ Creates and sets the style handler for the widget. Must
        be implemented by subclasses.

        """
        raise NotImplementedError

    def initialize_style(self):
        """ Initializes the style and style handler of a widget. Must
        be implemented by subclasses.

        """
        raise NotImplementedError

    def layout_child_widgets(self):
        """ Arranges the children of this component. Must be implemented
        by subclasses.

        """
        raise NotImplementedError
    
    def toolkit_widget(self):
        """ Returns the toolkit specific widget for this component.

        """
        return self.widget
    
    def parent_name_changed(self, name):
        """ The change handler for the 'name' attribute on the parent.
        QtComponent doesn't care about the name. Subclasses should
        reimplement if they need that info.

        """
        pass    

    #---------------------------------------------------------------------------
    # Implementation
    #---------------------------------------------------------------------------
    widget = Instance(QtCore.QObject)
        
    def parent_widget(self):
        """ Returns the logical QWidget parent for this component. 

        Since some parents may wrap non-Widget objects, this method will
        walk up the tree of parent components until a QWindow is found
        or None if no QWindow is found.

        Arguments
        ---------
        None

        Returns
        -------
        result : QWidget or None

        """
        # Our parent is a Component, and the parent of 
        # a Component is also a Component
        parent = self.parent
        while parent:
            widget = parent.toolkit_widget()
            if isinstance(widget, QtGui.QWidget):
                return widget
            parent = parent.parent
        
    def child_widgets(self):
        """ Iterates over the parent's children and yields the 
        toolkit widgets for those children.

        """
        for child in self.parent.children:
            yield child.toolkit_widget()

    #---------------------------------------------------------------------------
    # Implementation
    #---------------------------------------------------------------------------
