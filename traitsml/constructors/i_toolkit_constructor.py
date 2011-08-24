from traits.api import Interface, Instance, List, Tuple, Str

from ..interceptors.i_interceptor import IInterceptor


class IToolkitConstructor(Interface):
    """ The interface for defining toolkit constructors.

    An IToolkitConstructor object is responsible for creating a toolkit
    specific widget for a named element in a tml file. The constructors
    are composed together to create a constructor tree.

    Attributes
    ----------
    id : Str
        The unique identifier assigned to the widget, if any.

    metas : List(Instance(IToolkitConstructor))
        The list of constructor instances for any meta objects defined
        for this node of the TML tree.
    
    exprs : List(Tuple(Str, Instance(IInterceptor)))
        The list of tuples of info for intercepting traits on the 
        toolkit widget wrapper.

    children : List(Instance(IToolkitConstructor))
        The list of constructor instances for any children objects
        defined for this node of the TML tree.
    
    Methods
    -------
    toolkit_class()
        Imports and returns the toolkit specific wrapper class.

    __call__(**ctxt_objs)
        When called with context objects, should build an return
        an appropriate View object.
        
    """
    id = Str

    metas = List(Instance('IToolkitConstructor'))

    exprs = List(Tuple(Str, Instance(IInterceptor)))

    children = List(Instance('IToolkitConstructor'))

    def toolkit_class(self):
        """ Imports and returns the toolkit specific class.

        This method should import and return the class for intantiated
        the toolkit specific widget for this constructor. The import
        is done here to delay the import of any gui libraries for as
        long as possible.

        Arguments
        ---------
        None

        Returns
        -------
        result : Toolkit class
            The toolkit specific wrapper class for the widget.

        Raises
        ------
        None

        """
        raise NotImplementedError

    def __call__(self, **ctxt_objs):
        """ Called by the user with the desired scope objects.

        This method should actually build the toolkit specific ui
        tree using the provided ctxt_objs as the minimum global scope.
        The constructor is free to add items to the global scope 
        and create it's own local scopes as necessary before injecting
        the interceptors. It should return a View object properly 
        populated with the named widgets in the view. If a constructor
        is not a proper top level item and it's __call__ method is 
        called, then it should wrap itself in an appropraite default
        top-level container, and return the view for that.
        
        Arguments
        ---------
        **ctxt_objs
            Items that should appear in the global namespace of the 
            expressions.

        Returns
        -------
        result : View
            A properly instantiated View object that can be layed out and
            displayed by calling view.show(True)

        Raises
        ------
        XXX

        """
        raise NotImplementedError

