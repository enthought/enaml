from enthought.traits.api import (cached_property, HasStrictTraits, Instance, 
                                  List, Property)


class AbstractItem(HasStrictTraits):
    """ An abstract base class which implements the walking 
    and building of a toolkit tree. Meant to be inherited
    by classes which implement functionality.

    """
    # The underlying toolkit object which manages the toolkit widget
    toolkit_obj = Property
    
    # The children of the element, each with their own toolkt_obj
    children = List(Instance('AbstractItem'))
    
    #--------------------------------------------------------------------------
    # Layout Handling
    #--------------------------------------------------------------------------
    def init_widgets(self):
        # Notice that we're not calling init_widgets on the toolkit
        # obj, it's expected that toolkit obj come back through
        # us to get at the children.
        self.toolkit_obj.init_widget()
        for child in self.children:
            child.init_widgets()
    
    def init_attributes(self):
        # This is called after init_widgets since initializing the 
        # attributes will likely require the widget to exist.
        self.toolkit_obj.init_attributes()
        for child in self.children:
            child.init_attributes()

    def init_layout(self):
        # If a toolkit requires the widget to be displayed before applying
        # a layout (ala Qt), it should be done in the .init_layout() method.
        # This method should be called after calling .show()
        self.toolkit_obj.init_layout()
        for child in self.children:
            child.init_layout()

    def show(self):
        self.toolkit_obj.show()
    
    def hide(self):
        self.toolkit_obj.hide()

    #--------------------------------------------------------------------------
    # Property Handlers
    #--------------------------------------------------------------------------
    @cached_property
    def _get_toolkit_obj(self):
        if self.__class__ is AbstractItem:
            raise TypeError('Cannot create instances of AbstractItem.')
        # XXX I'm not sure if I like this...
        # XXX And we're creating a reference cycle.
        from . import toolkit_objs
        cls = getattr(toolkit_objs, self.__class__.__name__)
        return cls(abstract_obj=self)

    
