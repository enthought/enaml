import ast
import types
import weakref

from traits.api import (Any, CTrait, DelegatesTo, HasStrictTraits, Tuple,
                        HasTraits, Instance, Property, Str, implements,
                        cached_property)

from .i_interceptor import IInterceptor, IInterceptorFactory

from ..message import Message
from ..parsing.analyzer import AttributeVisitor


class BaseInterceptor(HasStrictTraits):

    # The code object that holds the expression
    code = Instance(types.CodeType)

    # The global namespace for the code.
    global_ns = Instance(dict)

    # The local namespace for the code.
    local_ns = Instance(dict)

    # The component object which we're intercepting
    obj = Property

    # The weakref to the obj (avoids a circular ref)
    _obj_ref = Instance(weakref.ref)

    # The trait name on the obj that we are intercepting
    name = Str

    #---------------------------------------------------------------------------
    # Property handlers
    #---------------------------------------------------------------------------
    def _get_obj(self):
        obj_ref = self._obj_ref
        if obj_ref is not None:
            return obj_ref()
    
    def _set_obj(self, obj):
        self._obj_ref = weakref.ref(obj)
    
    #---------------------------------------------------------------------------
    # Subclass helper methods
    #---------------------------------------------------------------------------
    def validate_injection(self, obj, name):
        """ Raises an error if any of the following conditions exist:
            
            * The trait has already been intercepted.
            * The object does not have a trait with the given name.
            * The trait is not suitable for intercepting.
            
        Returns a clone of the trait and the delegate name upon success.

        """
        trait = obj.trait(name)
        interceptor_name = '_%s_interceptor' % name

        if trait is None:
            msg = '`%s` is not a proper attribute on the `%s` object.'
            raise AttributeError(msg % (name, type(obj).__name__))

        if trait.type in ('property', 'event'):
            msg = 'The `%s` attr on the `%s` object cannot be intercepted.'
            raise TypeError(msg % (name, type(obj).__name__))

        if obj.trait(interceptor_name) is not None:
            msg = 'The `%s` attr on the `%s` object is already intercepted.'
            raise ValueError(msg % (name, type(obj).__name__))

        return trait(), interceptor_name


class NotifierInterceptor(BaseInterceptor):
    
    implements(IInterceptor)

    def inject(self, obj, name, global_ns, local_ns):
        self.obj = obj
        self.name = name
        self.global_ns = global_ns
        self.local_ns = local_ns
        obj.on_trait_change(self.notify, name)
        obj._interceptors.append(self)

    def notify(self, obj, name, old, new):
        local_ns = self.local_ns
        local_ns['msg'] = Message(obj, name, old, new)
        eval(self.code, self.global_ns, local_ns)


class DefaultInterceptor(BaseInterceptor):
    
    implements(IInterceptor)

    # The trait used to validate the values.
    validate_trait = Instance(CTrait)
    
    # The trait to which requests are redirected.
    value = Property(depends_on='_value')

    # The underlying value store.
    _value = Any

    def inject(self, obj, name, global_ns, local_ns):
        self.obj = obj
        self.name = name
        self.global_ns = global_ns
        self.local_ns = local_ns
        self.validate_trait, delegate_name = self.validate_injection(obj, name)

        obj.add_trait(delegate_name, self)
        obj.add_trait(name, DelegatesTo(delegate_name, 'value'))
        obj._interceptors.append(self)

        # Need to fire the trait_added or the delegate listeners 
        # don't get hooked up properly. 
        obj.trait_added = name

    def _get_value(self):
        return self._value
    
    def _set_value(self, val):
        val = self.validate_trait.validate(self.obj, self.name, val)
        self._value = val

    def __value_default(self):
        val = eval(self.code, self.global_ns, self.local_ns)
        val = self.validate_trait.validate(self.obj, self.name, val)
        return val


class BindingInterceptor(DefaultInterceptor):

    # The possible dependencies for this interceptor in the 
    # form ((root, (attr, attr, ...)), ...)
    deps = Tuple

    def inject(self, obj, name, global_ns, local_ns):
        super(BindingInterceptor, self).inject(obj, name, global_ns, local_ns)
        
        for obj_name, attrs in self.deps:

            try:
                obj = local_ns[obj_name]
            except KeyError:
                try:
                    obj = global_ns[obj_name]
                except KeyError:
                    msg = '`%s` is not defined or accessible in the namespace.'
                    raise NameError(msg % obj_name)

            if isinstance(obj, HasTraits):
                extended_name = '.'.join(attrs)
                obj.on_trait_change(self.refresh_value, extended_name)

    def refresh_value(self):
        val = eval(self.code, self.global_ns, self.local_ns)
        self.value = val


class DelegateInterceptor(DefaultInterceptor):
    
    implements(IInterceptor)

    # The name of the object to which we want to delegate in the ns.
    delegate_name = Str

    # The trait name on the object to which we are delegating.
    delegate_attr_name = Str

    # The object to which we are delegating.
    delegate_obj = Instance(HasTraits)
    
    def inject(self, obj, name, global_ns, local_ns):
        super(DelegateInterceptor, self).inject(obj, name, global_ns, local_ns)
        
        delegate_name = self.delegate_name
        try:
            obj = local_ns[delegate_name]
        except KeyError:
            try:
                obj = global_ns[delegate_name]
            except KeyError:
                msg = '`%s` is not defined or accessible in the namespace.'
                raise NameError(msg % delegate_name)

        self.delegate_obj = obj
        if isinstance(obj, HasTraits):
            obj.on_trait_change(self.refresh_value, self.delegate_attr_name)

    def _get_value(self):
        val = getattr(self.delegate_obj, self.delegate_attr_name)
        val = self.validate_trait.validate(self.obj, self.name, val)
        return val

    def _set_value(self, val):
        val = self.validate_trait.validate(self.obj, self.name, val)
        setattr(self.delegate_obj, self.delegate_attr_name, val)
        
    def __value_default(self):
        # Pull the default value via the property getter.
        return self._get_value()

    def refresh_value(self):
        # We just need to invalidate the 'value' property so its
        # listeners will pull new values. The property getter 
        # does the actual delegation.
        self._value = not self._value


class BaseInterceptorFactory(HasStrictTraits):

    ast = Instance(ast.Expression)

    code = Property(Instance(types.CodeType), depends_on='ast')

    dependencies = Property(Tuple, depends_on='ast')

    def __init__(self, ast):
        super(BaseInterceptorFactory, self).__init__()
        self.ast = ast

    @cached_property
    def _get_code(self):
        return compile(self.ast, 'TML', 'eval')

    @cached_property
    def _get_dependencies(self):
        visitor = AttributeVisitor()
        visitor.visit(self.ast)
        return visitor.results()
        

class Default(BaseInterceptorFactory):

    implements(IInterceptorFactory)

    def interceptor(self):
        return DefaultInterceptor(code=self.code)


class Bind(BaseInterceptorFactory):
    
    implements(IInterceptorFactory)

    def interceptor(self):
        return BindingInterceptor(code=self.code, deps=self.dependencies)


class Notify(BaseInterceptorFactory):

    implements(IInterceptorFactory)

    def interceptor(self):
        return NotifierInterceptor(code=self.code)


class Delegate(HasStrictTraits):

    implements(IInterceptorFactory)

    delegate_name = Str

    attr_name = Str

    def __init__(self, delegate_name, attr_name):
        super(Delegate, self).__init__()
        self.delegate_name = delegate_name
        self.attr_name = attr_name
        
    def interceptor(self):
        return DelegateInterceptor(delegate_name=self.delegate_name, 
                                   delegate_attr_name=self.attr_name)

