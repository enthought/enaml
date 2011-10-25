#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import weakref

from .qt.QtGui import QWidget

from ..component import AbstractTkComponent


class QtComponent(AbstractTkComponent):
    """ A Qt4 implementation of Component.

    A QtComponent is not meant to be used directly. It provides some 
    common functionality that is useful to all widgets and should 
    serve as the base class for all other classes. Note that this 
    is not a HasTraits class.

    """
    widget = None

    _shell_widget = lambda: None

    #--------------------------------------------------------------------------
    # Setup methods
    #--------------------------------------------------------------------------
    def create_widget(self):
        """ Creates the underlying Qt widget. Must be implemented by 
        subclasses.

        """
        raise NotImplementedError

    def initialize_widget(self):
        """ Initializes the attribtues of a wiget. Subclasses should 
        implement if they need to do widget initialization.

        """
        pass

    def initialize_layout(self):
        """ Arranges the children of this component. Subclasses should 
        implement if they need to do widget layout initialization.

        """
        pass
        
    def initialize_event_handlers(self):
        """ After the ui tree is fully initialized, this method
        is called to allow the widgets to bind their event handlers.

        """
        self.connect()

    #--------------------------------------------------------------------------
    # Implementation
    #--------------------------------------------------------------------------
    def connect(self):
        """ Implement this method in subclasses to connect to any necessary
        signals on the created widgets.

        """
        pass

    def _get_shell_widget(self):
        """ The shell_widget property getter which returns a strongref
        to the the shell widget.

        """
        return self._shell_widget()
    
    def _set_shell_widget(self, shell):
        """ The shell_widget property setter which stores a weakref
        to the shell widget.

        """
        self._shell_widget = weakref.ref(shell)

    shell_widget = property(_get_shell_widget, _set_shell_widget)
    
    @property
    def toolkit_widget(self):
        """ A property that returns the toolkit specific widget for this
        component.

        """
        return self.widget
    
    def shell_name_changed(self, name):
        """ The change handler for the 'name' attribute on the parent.
        QtComponent doesn't care about the name. Subclasses should
        reimplement if they need that info.

        """
        pass    
        
    def parent_widget(self):
        """ Returns the logical QWidget parent for this component. 

        Since some parents may wrap non-Widget objects, this method will
        walk up the tree of components until a QWidget is found or None 
        if no QWidget is found.

        Returns
        -------
        result : QWidget or None

        """
        shell_parent = self.shell_widget.parent
        while shell_parent:
            widget = shell_parent.toolkit_widget
            if isinstance(widget, QWidget):
                return widget
            shell_parent = shell_parent.parent
        
    def child_widgets(self):
        """ Iterates over the shell widget's children and yields the 
        toolkit widgets for those children.

        """
        for child in self.shell_widget.children:
            yield child.toolkit_widget

