from traits.api import Interface, Str, WeakRef, Instance

from ..enaml_base import EnamlBase
from ..style import StyleNode
from ..util.decorators import protected
from ..util.trait_types import ReadOnlyConstruct


class IComponentImpl(Interface):
    """ The base Component implementation interface.

    A component implementation is responsible for listening to attributes
    on the parent and doing conversions to and from those attributes
    and values on the widget. The implementation is added as a virtual
    listener on the component with a prefix of 'parent', so any 
    parent_*_changed methods will be called in response to a trait
    change on the parent. The implementation should set the traits
    on the parent (including events) when appropriate according to 
    their documentation.
 
    Attributes
    ----------
    parent : WeakRef(Component)
        A weak referent to the parent component.
        
    Methods
    -------
    set_parent(parent)
        Sets the parent to the parent component. This will be called by 
        the framework before the widget is to be created.
    
    create_widget()
        Creates the underlying toolkit widget.

    initialize_widget()
        Initializes the widget with attributes from the parent.
    
    layout_child_widgets()
        Add the child widgets of this component to any sizers or
        layout objects necessary to lay out the ui.

    toolkit_widget()
        Returns the toolkit specific widget.
    
    parent_name_changed(name)
        Called when the name trait on the parent changes.

    """
    parent = WeakRef('Component')

    def set_parent(self, parent):
        """ Sets the parent to the parent component. 

        This will be called by the framework before the widget is to be
        created. Typical implementations will just assign it to the 
        parent weakref. This is the first method called in the layout
        process.

        """
        raise NotImplementedError

    def create_widget(self):
        """ Creates the underlying toolkit widget. At the time this is
        called by the frameworks, the 'set_parent' method will have
        already been called. This is the second method called in the
        layout process.

        """
        raise NotImplementedError
    
    def initialize_widget(self):
        """ Initializes the widget with attributes from the parent. This
        is the third method called in the layout process.

        """
        raise NotImplementedError

    def layout_child_widgets(self):
        """ Adds the child widgets (if any) to any necessary layout
        components in the ui. This is the fourth and final method called
        in the layout process.

        """
        raise NotImplementedError

    def toolkit_widget(self):
        """ Returns the toolkit specific widget being mangaged by this
        implementation object.

        """
        raise NotImplementedError

    def parent_name_changed(self, name):
        """ Called when the name on the component changes.

        """
        raise NotImplementedError


@protected('style', 'toolkit_impl')
class Component(EnamlBase):
    """ The most base class of the Enaml widgets component heierarchy. 
    
    All Enaml  widget classes should inherit from this class. This class
    is not meant to be instantiated.
    
    Attributes
    ----------
    name : Str
        The name of this element which may be used as metainfo by other
        components. Note that this is not the same as the identifier 
        that can be assigned to a component as part of the enaml grammar.

    style : Instance(StyleNode)
        A protected read-only attribute that holds the component's style
        node.

    toolkit_impl : Instance(ComponentImpl)
        The toolkit specific object that implements the behavior of 
        this component. This implementation object is added as a virtual 
        listener for this component and maintains a weak reference to 
        this component. The listeners are set up and torn down with the 
        'hook_impl' and 'unhook_impl' methods. This is a protected 
        attribute.

    Methods
    -------
    layout()
        Lay out and create the widgets for this component and it's
        children. This builds the widget tree.
    
    toolkit_widget()
        Returns the underlying gui toolkit widget which is being 
        managed by the implemention object.
    
    refresh(force=False)
        Refreshes the ui tree from this point down, rebuilding children 
        where necessary.

    """
    name = Str

    style = ReadOnlyConstruct(lambda self, name: StyleNode(parent=self))

    toolkit_impl = Instance(IComponentImpl)

    def layout(self):
        """ Initialize and layout the component and it's children. 

        In addition to running the layout process, this method calls
        hook_impl() which will add the implementation as a virtual 
        listen on this instance. This method should not typically be 
        called by user code.

        Arguments
        ---------
        None

        Returns
        -------
        result : None

        """
        impl = self.toolkit_impl
        impl.set_parent(self)
        impl.create_widget()
        for child in self.children:
            child.layout()
        impl.initialize_widget()
        impl.layout_child_widgets()
        self._hook_impl()
        
    def toolkit_widget(self):
        """ Returns the toolkit specific widget for this component.

        """
        return self.toolkit_impl.toolkit_widget()

    def refresh(self, force=False):
        """ Refreshes the layout. 

        """
        pass

    def _hook_impl(self):
        """ Adds the implementation object as a listener via the 
        'add_trait' method.
        
        """
        self.add_trait_listener(self.toolkit_impl, 'parent')

