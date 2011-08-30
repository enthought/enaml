from traits.api import Interface, Instance, List, Tuple, Str

from ..interceptors.i_interceptor import IInterceptorFactory


class IToolkitConstructor(Interface):
    """ The IToolkitConstructor interface for toolkit constructors.

    An IToolkitConstructor object is responsible for creating a toolkit
    specific widget for a named element in a tml file. The constructors
    are composed together to create a constructor tree. The root 
    of the constructor tree is callable with context objects as 
    arguments, and should return a traitsml.view.View instance.

    Attributes
    ----------
    identifier : Str
        The unique identifier assigned to the widget (if any).
        An empty string is considered to be no id.

    metas : List(Instance(IToolkitConstructor))
        The list of constructor instances for any meta objects defined
        for this node of the TML tree.
    
    exprs : List(Tuple(Str, Instance(IInterceptorFactory)))
        The list of tuples of info for intercepting traits on the 
        toolkit widget wrapper. The string is the name of the 
        trait to be intercepted and the object is an interceptor
        factory which will create an interceptor on demand.

    children : List(Instance(IToolkitConstructor))
        The list of constructor instances for any child objects
        defined for this node of the TML tree.
    
    Methods
    -------
    toolkit_class()
        Imports and returns the toolkit specific wrapper class.

    __call__(**ctxt_objs)
        When called with context objects, should build an return
        an appropriate traitsml.view.View object.
        
    """
    identifier = Str

    metas = List(Instance('IToolkitConstructor'))

    exprs = List(Tuple(Str, Instance(IInterceptorFactory)))

    children = List(Instance('IToolkitConstructor'))

    def toolkit_class(self):
        """ Imports and returns the toolkit specific class.

        This method should import and return the class for creating
        the toolkit specific widget for this constructor. The import
        is done here to delay the import of any gui libraries for as
        long as possible.

        Arguments
        ---------
        None

        Returns
        -------
        result : Toolkit class
            The toolkit specific wrapper class for the widget that
            this constructor creates.

        Raises
        ------
        None

        """
        raise NotImplementedError

    def __call__(self, **ctxt_objs):
        """ Called by the user with the desired scope objects.

        This method performs the actual building of the toolkit specific 
        ui tree using the provided ctxt_objs as the minimum global scope.
        The constructor is free to add items to the global scope and to 
        create it's own local scopes as necessary before injecting the 
        interceptors onto the ui objects. If a constructor is not a proper 
        top level item and it's __call__ method is called, then it should 
        wrap itself in an appropraite default top-level container, and 
        return the view for that.
        
        Arguments
        ---------
        **ctxt_objs
            Items that should appear in the global namespace of the 
            expressions.

        Returns
        -------
        result : traitsml.view.View
            A properly instantiated View object that can be layed out and
            displayed by calling view.show(True)

        """
        raise NotImplementedError

