from abc import ABCMeta, abstractmethod

from traits.api import Any

from ..expressions import ExpressionDefaultTrait


class AbstractSetupHook(object):
    """ An abstract base class that defines the methods that need to 
    be implemented by a setup hook that is used by a Component during
    the setup process.

    """
    __metaclass__ = ABCMeta

    __slots__ = ()
    
    @abstractmethod
    def create(self, component):
        raise NotImplementedError
    
    @abstractmethod
    def initialize(self, component):
        raise NotImplementedError

    @abstractmethod
    def bind(self, component):
        raise NotImplementedError


class NullSetupHook(AbstractSetupHook):
    """ An AbstractSetupHook implementation that does nothing. This 
    makes is easy for hooks that only need to implement a few methods 
    to subclass from this and implement only what is needed.

    """
    __slots__ = ()
    
    def create(self, component):
        yield

    def initialize(self, component):
        yield

    def bind(self, component):
        yield


class ExpressionSetupHook(NullSetupHook):

    __slots__ = ('name', 'expression', 'eval_default')

    def __init__(self, name, expression, eval_default=True):
        self.name = name
        self.expression = expression
        self.eval_default = eval_default

    def create(self, component):
        # We want to setup the expressions before we create and
        # initialize the widgets so that default value computations
        # will work properly. However, we don't want to bind to 
        # changes in the expression just yet.
        self.setup_expression(component)
        
        # Yield back to the framework so it can create the widgets in 
        # the tree.
        yield

        # No that the widgets are created, but not initialized, we
        # bind the expression so that changes to the widget during
        # its initialization is reflected in the shell widget
        self.bind_expression(component)

    def setup_expression(self, component):
        """ Sets up the expression for use on a component. This involves
        adding special temporary instance traits to the component so 
        that the default value is properly retrieved from the expression.

        """
        name = self.name
        expression = self.expression
        eval_default = self.eval_default

        # If the trait is in class traits, then we need to add an 
        # instance trait temporarily in order to handle the default
        # value initialization. Unlike the instance trait cases which
        # are handled below, there is some notifier management that 
        # needs to take place here and that's why this case is handled
        # by a special trait type.
        if name in component.class_traits():
            if eval_default:
                component.add_trait(name, ExpressionDefaultTrait(expression))
        
        # Otherwise, the user is defining their own attributes and we 
        # need to create an instance trait (if necessary) and then bind 
        # the default value (also if necessary). Note that the .add_trait
        # method automatically clones the trait before adding it to 
        # the instance trait dict. This means that the default value
        # handler must be applied *before* the call to .add_trait.
        # We don't need to be rigorous or handle the notifiers like
        # we do in `_set_default_handler` because the .add_trait method
        # handles the notifier management for us.
        else:
            trait = component._instance_traits().get(name)
            if trait is None:
                trait = Any().as_ctrait()
            if eval_default:
                dvf = lambda obj: expression.eval_expression()
                trait.default_value(8, dvf)
            component.add_trait(name, trait)

    def bind_expression(self, component):
        """ Calls the bind method of the expression object. This is
        performed after all of the other expressions have been set up
        so that the notifiers resolve correctly.

        """
        self.expression.bind()

