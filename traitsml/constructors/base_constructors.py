from traits.api import HasStrictTraits, List, Instance, Tuple, Str, Any

from .i_toolkit_constructor import IToolkitConstructor

from ..interceptors.i_interceptor import IInterceptorFactory


class BaseToolkitCtor(HasStrictTraits):

    identifier = Str

    metas = List(Instance(IToolkitConstructor))

    exprs = List(Tuple(Str, Instance(IInterceptorFactory)))

    children = List(Instance(IToolkitConstructor))
    
    # The transient traits that are reset in the cleanup method.
    impl = Any

    local_ns = Instance(dict, ())

    global_ns = Instance(dict)

    def construct(self):
        for meta in self.metas:
            meta.construct()
        for child in self.children:
            child.construct()
        cls = self.toolkit_class()
        self.impl = cls()

    def build_ns(self, global_ns, parent=None):
        impl = self.impl
        
        local_ns = self.local_ns
        local_ns['self'] = impl
        local_ns['parent'] = parent.impl if parent is not None else None

        identifier = self.identifier
        if identifier:
            if identifier in global_ns:
                msg = 'The name %s already exists in the namespace.'
                raise NameError(msg % identifier)
            else:
                global_ns[identifier] = impl
        
        for meta in self.metas:
            meta.build_ns(global_ns, self)
        for child in self.children:
            child.build_ns(global_ns, self)

        self.global_ns = global_ns

    def inject_interceptors(self):
        impl = self.impl
        global_ns = self.global_ns
        local_ns = self.local_ns
        for name, interceptor_factory in self.exprs:
            interceptor = interceptor_factory.interceptor()
            interceptor.inject(impl, name, global_ns, local_ns)
        
        for meta in self.metas:
            meta.inject_interceptors()
        for child in self.children:
            child.inject_interceptors()

    def cleanup(self):
        self.impl = None
        self.local_ns = {}
        for meta in self.metas:
            meta.cleanup()
        for child in self.children:
            child.cleanup()

    def __call__(self, **ctxt_objs):
        self.construct()
        self.build_ns(ctxt_objs)
        self.inject_interceptors()
        res = self.build_view()
        self.cleanup()
        return res

    def toolkit_class(self):
        raise NotImplementedError

    def build_view(self):
        raise NotImplementedError
    

class BaseComponentCtor(BaseToolkitCtor):

    def construct(self):
        super(BaseComponentCtor, self).construct()
        impl = self.impl
        for meta in self.metas:
            impl.add_meta_info(meta.impl)


class BasePanelCtor(BaseComponentCtor):

    def construct(self):
        super(BasePanelCtor, self).construct()
        children = self.children
        if children:
            if len(children) > 1:
                msg = '%s type can have 1 (and only 1) container.'
                raise ValueError(msg % type(self.impl))
            else:
                self.impl.set_container(children[0].impl)


class BaseContainerCtor(BaseComponentCtor):

    def construct(self):
        super(BaseContainerCtor, self).construct()
        impl = self.impl
        for child in self.children:
            impl.add_child(child.impl)


class BaseElementCtor(BaseComponentCtor):

    def construct(self):
        super(BaseElementCtor, self).construct()
        if self.children:
            msg = '%s type cannot have children.' % type(self.impl)
            raise ValueError(msg)

