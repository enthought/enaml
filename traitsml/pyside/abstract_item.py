from enthought.traits.api import Any, HasStrictTraits


class AbstractItem(HasStrictTraits):

    # The parent abstract toolkit obj to which we delegate our stuff
    abstract_obj = Any

    # The underlying Qt widget (should be a subclass of QWidget)
    widget = Any
    
    #--------------------------------------------------------------------------
    # Creation Handlers
    #--------------------------------------------------------------------------
    def create_widget(self):
        # Create and return a QWidget for the instance.
        raise TypeError('AbstractItem cannot create a widget.')
    
    #--------------------------------------------------------------------------
    # Layout Handler
    #--------------------------------------------------------------------------
    def layout_children(self):
        raise TypeError('AbstractItem cannot lay out children.')

    #--------------------------------------------------------------------------
    # Initialization Handlers
    #--------------------------------------------------------------------------
    def init_widget(self):
        raise TypeError('AbstractItem cannot initialize a widget.')
    
    def init_attributes(self):
        raise TypeError('AbstractItem cannot intitalize attributes.')

    def init_layout(self):
        raise TypeError('AbstractItem cannot be initialize a layout.')

    def show(self):
        self.widget.show()
    
    def hide(self):
        self.widget.hide()

    
