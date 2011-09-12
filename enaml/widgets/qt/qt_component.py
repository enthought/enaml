from traits.api import implements, HasStrictTraits, WeakRef

from ..component import Component, IComponentImpl


class QtComponent(HasStrictTraits):
    """ A PySide implementation of Component.

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
    parent = WeakRef('Component')

    def set_parent(self, parent):
        """ Sets the parent to the parent component. 

        """
        

    def create_widget(self):
        """ Creates the underlying toolkit widget.
        
        """
        
    
    def initialize_widget(self):
        """ Initializes the widget with attributes from the parent.

        """
        

    def layout_child_widgets(self):
        """ Adds the child widgets (if any) to any necessary layout
        components in the ui

        """
        

    def toolkit_widget(self):
        """ Returns the toolkit specific widget being mangaged by this
        implementation object.

        """
        
		
    def parent_name_changed(self, name):
        """ Called when the name on the component changes.

        """
        
