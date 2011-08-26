import ast
import types

from traits.api import (Any, CTrait, DelegatesTo, HasStrictTraits, Tuple,
                        HasTraits, Instance, Property, Str, implements,
                        cached_property)

from .i_interceptor import IInterceptor, IInterceptorFactory

from ..parsing.analyzer import AttributeVisitor


class Arguments(object):

    __slots__ = ('obj', 'name', 'old', 'new')

    def __init__(self, obj, name, old, new):
        self.obj = obj
        self.name = name
        self.old = old
        self.new = new


class InjectionMixin(object):
    """ A mixin to help the interception process. """

    def inject_delegate(self, obj, name, delegate_name, delegate_attr_name):
        obj.add_trait(delegate_name, self)
        obj.add_trait(name, DelegatesTo(delegate_name, delegate_attr_name))
        obj.trait_added = name

    def valid_injection(self, obj, name):
        """ Raises an error if the trait_name on obj does not exist
        or is not suitable for intercepting. Returns a clone of the
        trait when successful.

        """
        trait = obj.trait(name)
        if trait is None:
            msg = '`%s` is not trait on the %s object.'
            raise AttributeError(msg % (name, type(obj).__name__))
        elif trait.type == 'property':
            msg = 'Cannot intercept `%s` trait, which is a Property.'
            raise TypeError(msg % name)
        elif trait.type == 'event':
            msg = 'Cannot intercept `%s` trait, which is an Event.'
            raise TypeError(msg % name)
        return trait()


class CodeInterceptor(HasStrictTraits):

    # The code object that holds the expression.
    code = Instance(types.CodeType)

    # The global namespace for the code. 
    global_ns = Instance(dict)

    # The local namespace for the code.
    local_ns = Instance(dict)


class NotifierInterceptor(CodeInterceptor):
    
    implements(IInterceptor)

    def inject(self, obj, name, global_ns, local_ns):
        self.global_ns = global_ns
        self.local_ns = local_ns
        obj.on_trait_change(self.notify, name)

        # We need to add ourselves to the obj so that a strong
        # ref is mantained and we don't get gc'd. We have other
        # options about where to put the strong ref, but this
        # is consistent with the style of the other interceptors.
        i_name = '_notifier_interceptor_%s' % name
        obj.add_trait(i_name, self)

    def notify(self, obj, name, old, new):
        args = Arguments(obj, name, old, new)
        local_ns = self.local_ns
        local_ns['args'] = args
        eval(self.code, self.global_ns, local_ns)


class DefaultInterceptor(CodeInterceptor, InjectionMixin):
    
    implements(IInterceptor)

    # The trait used to validate the values.
    validate_trait = Instance(CTrait)
    
    # The actual trait that holds the value.
    value = Property(depends_on='_value')

    _value = Any

    def inject(self, obj, name, global_ns, local_ns):
        self.global_ns = global_ns
        self.local_ns = local_ns
        self.validate_trait = self.valid_injection(obj, name)
        delegate_name = '_%s_%s' % (name, self.__class__.__name__)
        self.inject_delegate(obj, name, delegate_name, 'value')

    def _get_value(self):
        return self._value
    
    def _set_value(self, val):
        val = self.validate_trait.validate(self, 'value', val)
        self._value = val

    def __value_default(self):
        val = eval(self.code, self.global_ns, self.local_ns)
        val = self.validate_trait.validate(self, 'value', val)
        return val


class BindingInterceptor(DefaultInterceptor, InjectionMixin):

    # The possible dependencies for this interceptor in the 
    # form ((root, (leaf, leaf,...)),...)
    deps = Tuple

    def inject(self, obj, name, global_ns, local_ns):
        super(BindingInterceptor, self).inject(obj, name, global_ns, local_ns)
        for obj_name, attrs in self.deps:
            obj = local_ns.get(obj_name) or global_ns.get(obj_name)
            if obj is None:
                msg = '`%s` is not defined or accessible in the namespace.'
                raise NameError(msg % obj_name)
            else:
                if isinstance(obj, HasTraits):
                    extended_name = '.'.join(attrs)
                    obj.on_trait_change(self.update_value, extended_name)

    def update_value(self):
        val = eval(self.code, self.global_ns, self.local_ns)
        self.value = val 


class DelegateInterceptor(DefaultInterceptor, InjectionMixin):
    
    # The name of the object to which we want to delegate in the ns.
    obj_name = Str

    # The trait name on the object to which we are delegating.
    trait_name = Str

    # The object to which we are delegating.
    obj = Instance(HasTraits)
    
    def inject(self, obj, name, global_ns, local_ns):
        super(DelegateInterceptor, self).inject(obj, name, global_ns, local_ns)
        obj_name = self.obj_name
        obj = local_ns.get(obj_name) or global_ns.get(obj_name)
        if obj is None:
            msg = '`%s` is not defined or accessible in the namespace.'
            raise NameError(msg % obj_name)
        else:
            self.obj = obj
            if isinstance(obj, HasTraits):
                obj.on_trait_change(self.update_value, self.trait_name)

    def _get_value(self):
        val = getattr(self.obj, self.trait_name)
        val = self.validate_trait.validate(self, 'value', val)
        return val

    def _set_value(self, val):
        setattr(self.obj, self.trait_name, val)
        
    def update_value(self):
        self._value = not self._value


class CodeInterceptorFactory(HasStrictTraits):

    ast = Instance(ast.Expression)

    code = Property(Instance(types.CodeType), depends_on='ast')

    dependencies = Property(Tuple, depends_on='ast')

    def __init__(self, ast):
        super(CodeInterceptorFactory, self).__init__()
        self.ast = ast

    @cached_property
    def _get_code(self):
        return compile(self.ast, 'TML', 'eval')

    @cached_property
    def _get_dependencies(self):
        visitor = AttributeVisitor()
        visitor.visit(self.ast)
        return visitor.results()
        

class Default(CodeInterceptorFactory):

    implements(IInterceptorFactory)

    def interceptor(self):
        return DefaultInterceptor(code=self.code)


class Bind(CodeInterceptorFactory):
    
    implements(IInterceptorFactory)

    def interceptor(self):
        return BindingInterceptor(code=self.code, deps=self.dependencies)


class Notify(CodeInterceptorFactory):

    implements(IInterceptorFactory)

    def interceptor(self):
        return NotifierInterceptor(code=self.code)


class Delegate(HasStrictTraits):

    implements(IInterceptorFactory)

    obj_name = Str

    attr_name = Str

    def __init__(self, obj_name, attr_name):
        super(Delegate, self).__init__(obj_name=obj_name, attr_name=attr_name)
        
    def interceptor(self):
        obj_name = self.obj_name
        trait_name = self.attr_name
        return DelegateInterceptor(obj_name=obj_name, trait_name=trait_name)

    