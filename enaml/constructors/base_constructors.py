from traits.api import HasStrictTraits, List, Instance, Tuple, Str

from .i_toolkit_constructor import IToolkitConstructor

from ..expression_delegates import (IExpressionDelegateFactory, 
                                    IExpressionNotifierFactory)
from ..widgets.component import Component


class BaseToolkitCtor(HasStrictTraits):

    identifier = Str

    delegates = List(Tuple(Str, Instance(IExpressionDelegateFactory)))

    notifiers = List(Tuple(Str, Instance(IExpressionNotifierFactory)))

    metas = List(Instance(IToolkitConstructor))

    children = List(Instance(IToolkitConstructor))
    
    #---------------------------------------------------------------------------
    # Transient traits that are reset in the cleanup method.
    #---------------------------------------------------------------------------
    impl = Instance(Component)

    local_ns = Instance(dict, ())

    global_ns = Instance(dict)

    def construct(self):
        self.impl = impl = self.component()
        for meta in self.metas:
            meta.construct()
            impl.add_meta_info(meta.impl)
        for child in self.children:
            child.construct()
            impl.add_child(child.impl)

    def build_ns(self, global_ns):
        impl = self.impl
        self.local_ns['self'] = impl
        identifier = self.identifier
        if identifier:
            if identifier in global_ns:
                msg = 'The name %s already exists in the namespace.'
                raise NameError(msg % identifier)
            else:
                global_ns[identifier] = impl
        for meta in self.metas:
            meta.build_ns(global_ns)
        for child in self.children:
            child.build_ns(global_ns)
        self.global_ns = global_ns

    def hook_delegates_and_notifiers(self):
        impl = self.impl
        global_ns = self.global_ns
        local_ns = self.local_ns
        for attr, delegate_factory in self.delegates:
            delegate = delegate_factory(global_ns, local_ns)
            impl.delegate_attribute(attr, delegate)
        for attr, notifier_factory in self.notifiers:
            notifier = notifier_factory(global_ns, local_ns)
            impl.notify_attribute(attr, notifier)        
        for meta in self.metas:
            meta.hook_delegates_and_notifiers()
        for child in self.children:
            child.hook_delegates_and_notifiers()

    def cleanup(self):
        self.impl = None
        self.local_ns = {}
        self.global_ns = {}
        for meta in self.metas:
            meta.cleanup()
        for child in self.children:
            child.cleanup()

    def __call__(self, **ctxt_objs):
        self.construct()
        self.build_ns(ctxt_objs)
        self.hook_delegates_and_notifiers()
        res = self.build_view()
        self.cleanup()
        return res

    def component(self):
        raise NotImplementedError

    def build_view(self):
        raise NotImplementedError

