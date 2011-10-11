#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import (HasStrictTraits, Instance, Dict, Str, List, Any, 
                        TraitChangeNotifyWrapper)

from .expressions import IExpressionBinder


def _set_default_handler(obj, name, binder):
    """ Sets up a handler that uses an expression binder to compute the
    default value of a class trait attribute. This is meant for use with 
    instances of EnamlBase.

    Arguments
    ---------
    obj : Instance(EnamlBase)
        The EnamlBase instance which holds the attribute we're binding.
    
    name : string
        The name of the attribute on the instance for which we want to
        handle default values.
    
    binder : Instance(IExpressionBinder)
        An instance of an expression binder that will give use the 
        default value.

    Notes
    -----
    This function works by temporarily adding an instance trait to the
    object which is removed as soon as the default value is computed.

    """
    def rebind(rebind_obj, rebind_name, notifier):
        """ Rebinds a trait notifier by reconstituting the handler and 
        calling on_trait_change to create the new notifier. Currently
        only handles TraitChangeNotifyWrappers.

        """
        if isinstance(notifier, TraitChangeNotifyWrapper):
            call_method = notifier.call_method
            if call_method.startswith('call_'):
                handler = notifier.handler
            elif call_method.startswith('rebind_call_'):
                # The handler object is stored as a weakref
                handler_obj = notifier.object()
                if handler_obj is None:
                    return
                handler_name = notifier.name
                handler = getattr(handler_obj, handler_name)
            else:
                msg = 'unknown call method `%s`' % call_method
                raise ValueError(msg)
            rebind_obj.on_trait_change(handler, rebind_name)

    def default_value(default_obj):
        """ A default value handler closure that removes the instance
        trait as soon as the default value is computed.

        """
        # The standard `remove_trait` method of the HasTraits class
        # doesn't copy over any instance notifiers (as it shouldn't).
        # But, we need that behavior here since the instance trait is
        # intended to be transparent.
        instance_trait = default_obj._instance_traits().get(name)
        if instance_trait is not None:
            default_obj.remove_trait(name)
            instance_notifiers = instance_trait._notifiers(0)
            if instance_notifiers is not None:
                class_trait = default_obj.trait(name)
                if class_trait is not None:
                    for notifier in instance_notifiers:
                        rebind(default_obj, name, notifier)
        
        # We do a setattr followed by a getattr in case the thing we
        # are grabbing the default value for is a Property or a delegate.
        # In effect, we are mimicking the user evaluating the expression 
        # and setting the value on the attribute.
        val = binder.eval_expression()
        setattr(default_obj, name, val)
        res = getattr(default_obj, name, val)
        
        return res

    # This is the temporary instance trait that is removed by the
    # `default_value` closure
    itrait = Any().as_ctrait()
    itrait.default_value(8, default_value)
    obj.add_trait(name, itrait)


class EnamlBase(HasStrictTraits):
    """ The most base class of types used in Enaml source files.

    Attributes
    ----------
    _expression_binders : Dict(Str, List(Instance(IExpressionBinder)))
        The dictionary of expression binding objects. Used internally
        by the instance.

    Methods
    -------
    add_expression_binder(name, binder, eval_default=True)
        Add an expression binder to the instance.

    bind_expressions()
        Trigger the binding operation of the expression binder objects.

    """
    _expression_binders = Dict(Str, List(Instance(IExpressionBinder)))

    @classmethod
    def protect(cls, *names):
        protected = set(names)
        try:
            protected.update(cls.__protected__)
        except AttributeError:
            pass
        cls.__protected__ = protected

    def add_expression_binder(self, name, binder, eval_default=True):
        """ Add an expression binder to the instance.

        Arguments
        ---------
        name : string
            The name of the trait attribute on the instance to which we
            want to bind the expression.
        
        binder : Instance(IExpressionBinder)
            The expression binder instance that will be bound to the
            attribute.
        
        eval_default : bool, optional
            Whether or not to evaluate the expression and use the result
            as a default value. Defaults to True.

        """
        self._expression_binders.setdefault(name, []).append(binder)
        
        # If the trait is in class traits, then we need to add an 
        # instance trait temporarily in order to handle the default
        # value initialization. Unlike the instance trait cases which
        # are handled below, there is some notifier management that 
        # needs to take place here and that's why this case is handled
        # by an external function, rather than obfuscating the main
        # idea and readability here.
        if name in self.class_traits():
            if eval_default:
                _set_default_handler(self, name, binder)
        
        # Otherwise, the user is defining their own attributes and we 
        # need to create an instance (if necessary) and then bind the 
        # default value (also if necessary). Note that the .add_trait
        # method automatically clones the trait before adding it to 
        # the instance trait dict. This means that the default value
        # handler must be applied *before* the call to .add_trait.
        # We don't need to be rigorous or handle the notifiers like
        # we do in `_set_default_handler` because the .add_trait method
        # handles the notifier management for us.
        else:
            trait = self._instance_traits().get(name)
            if trait is None:
                trait = Any().as_ctrait()
            if eval_default:
                dvf = lambda obj: binder.eval_expression()
                trait.default_value(8, dvf)
            self.add_trait(name, trait)

    def bind_expressions(self):
        """ Trigger the binding operation of the expression binders.

        Call this method after all binder objects have been added via
        the `add_expression_binder` method and *after* any other objects
        in the tree have been created (ala delayed binding). This will 
        cause the binder object to hookup any required listeners on the 
        object tree.

        """
        for name, binders in self._expression_binders.iteritems():
            for binder in binders:
                binder.bind(self, name)


EnamlBase.protect('_expression_binders')

