import ast
import types

from traits.api import implements, HasStrictTraits, Instance, Property, Tuple

from .i_interceptor_factory import IInterceptorFactory
from .traits_code_interceptors import (NotifierInterceptor, DefaultInterceptor,
                                       BindingInterceptor, DelegateInterceptor)

from ..parsing.analyzer import AttributeVisitor


class CodeInterceptorFactory(HasStrictTraits):

    ast = Instance(ast.Expression)

    code = Property(types.CodeType, depends_on='ast')

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
        return visit.results()
        

class Default(CodeInterceptorFactory):

    implements(IInterceptorFactory)

    def interceptor(self):
        return DefaultInterceptor(code=self.code)


class Bind(CodeInterceptorFactory):
    
    implements(IInterceptorFactory)

    def interceptor(self):
        return BindingInterceptor(code=self.code, deps=self.dependencies)


class Delegate(CodeInterceptorFactory):

    implements(IInterceptorFactory)

    def interceptor(self):
        deps = self.dependencies
        if len(deps) != 1 or len(deps[0][1]) != 1:
            raise ValueError('Invalid delegation expression %s.' % deps)
        obj_name, leaves = deps
        trait_name = leaves[0]
        return DelegateInterceptor(obj_name=obj_name, trait_name=trait_name)


class Notify(CodeInterceptorFactory):

    implements(IInterceptorFactory)

    def interceptor(self):
        return NotifierInterceptor(code=self.code)

