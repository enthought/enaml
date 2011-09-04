from traits.api import Interface, Instance, List, Tuple, Str

from ..expression_delegates import (IExpressionDelegateFactory, 
                                    IExpressionNotifierFactory)


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

    delegates : List(Tuple(Str, Instance(IExpressionDelegateFactory)))
        The list of tuples of info for delegating traits on the toolkit 
        widget wrapper. The string is the name of the trait to be 
        delegated and the object is an expression delegate factory which 
        will create a delegate on demand.
    
    notifiers : List(Tuple(Str, Instance(IExpressionNotifierFactory)))
        The list of tuples of info for setting notifiers on the widget
        wrapper. The string is the name of the trait on which we want
        notifications and the object is an expression notifier factory 
        which will create a notifier on demand.

    metas : List(Instance(IToolkitConstructor))
        The list of constructor instances for any meta objects defined
        for this node of the TML tree.
    
    children : List(Instance(IToolkitConstructor))
        The list of constructor instances for any child objects
        defined for this node of the TML tree.
    
    Methods
    -------
    component()
        Imports, instantiates, and returns the toolkit specific component.

    __call__(**ctxt_objs)
        When called with context objects, should build an return
        an appropriate traitsml.view.View object.
        
    """
    identifier = Str

    delegates = List(Tuple(Str, Instance(IExpressionDelegateFactory)))

    notifiers = List(Tuple(Str, Instance(IExpressionNotifierFactory)))

    metas = List(Instance('IToolkitConstructor'))

    children = List(Instance('IToolkitConstructor'))

    def component(self):
        """ Imports, instantiates, and returns the toolkit component.

        This method should import, instantiate, and return a toolkit 
        specific component. This will typically be a pair of objects:
        the abstract widget object, and its implementation child.
        Though, this is not required and custom widgets may be implemented
        more simply. The import is done here to delay the import of any gui 
        libraries for as long as possible.

        Arguments
        ---------
        None

        Returns
        -------
        result : Component 
            A toolkit specific component.

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
        result : View
            A properly instantiated View object that can be layed out and
            displayed by calling view.show()

        """
        raise NotImplementedError

