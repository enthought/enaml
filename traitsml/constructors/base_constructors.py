from traits.api import HasStrictTraits, List, Instance, Tuple, Str, Any

from .i_toolkit_constructor import IToolkitConstructor

from ..interceptors.i_interceptor import IInterceptor


class BaseToolkitCtor(HasStrictTraits):

    id = Str

    metas = List(Instance(IToolkitConstructor))

    exprs = List(Tuple(Str, Instance(IInterceptor)))

    children = List(Instance(IToolkitConstructor))
    
    # The transient traits that are reset in the cleanup method.
    impl = Any

    local_ns = Instance(dict)

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

        name = self.id
        if name:
            if name in global_ns:
                msg = 'The name %s already exists in the namespace.' % name
                raise NameError(msg)
            else:
                global_ns[name] = impl
        
        for meta in self.metas:
            meta.build_ns(global_ns, self)
        for child in self.children:
            child.build_ns(global_ns, self)

    def inject_interceptors(self):
        impl = self.impl
        global_ns = self.global_ns
        local_ns = self.local_ns
        for name, interceptor in self.exprs:
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
        for child in self.children():
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


class BaseWindowCtor(BaseComponentCtor):

    def construct(self):
        super(BaseWindowCtor, self).construct()
        children = self.children
        if children:
            if len(children) > 1:
                msg = 'A Window may have 1 (and only 1) container.'
                raise ValueError(msg)
            else:
                self.impl.set_container(children[0].impl)


class BaseContainerCtor(BaseComponentCtor):

    def construct(self):
        super(BaseContainerCtor, self).construct()
        impl = self.impl
        for child in self.children:
            impl.add_child(child)


class BaseElementCtor(BaseComponentCtor):

    def construct(self):
        super(BaseElementCtor, self).construct()
        if self.children:
            msg = 'Element %s cannot have children.' % type(self.impl)
            raise ValueError(msg)

