#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits import api as t_types

from . import enaml_ast
from . import byteplay

from .. import imports
from ..toolkit import Toolkit, Constructor
from ..widgets.base_component import BaseComponent


#: Common Python builtin types mapped to their traits equivalent.
_BUILTIN_TYPE_MAPPING = {
    bool: t_types.Bool,
    int: t_types.Int,
    long: t_types.Long,
    float: t_types.Float,
    complex: t_types.Complex,
    str: t_types.Str,
    unicode: t_types.Unicode,
    object: t_types.Any,
    list: t_types.Instance(list, ()),
    set: t_types.Instance(set, ()),
    dict: t_types.Instance(dict, ()),
    tuple: t_types.Instance(tuple, ()),
}


#------------------------------------------------------------------------------
# Node Visitor
#------------------------------------------------------------------------------
class _NodeVisitor(object):
    """ A node visitor class that is used as base class for the various
    Enaml compilers.

    """
    def visit(self, node):
        """  The main visitor dispatch method.

        """
        name = 'visit_%s' % node.__class__.__name__
        try:
            method = getattr(self, name)
        except AttributeError:
            method = self.default_visit
        method(node)

    def default_visit(self, node):
        """ The default visitor method. Raises an error since there 
        should not be any unhandled nodes.

        """
        raise ValueError('Unhandled Node %s.' % node)


#------------------------------------------------------------------------------
# Compiler Runtime Helper Functions
#------------------------------------------------------------------------------
def _compiler_load_operator(operator_name):
    """ A compiler runtime function which is used to lookup a named 
    operator from the active toolkit.

    """
    tk = Toolkit.active_toolkit()
    try:
        operator = tk[operator_name]
    except KeyError:
        # XXX to an translation from operator name -> symbol
        msg = 'The %s operator is not defined in the active toolkit.'
        raise ValueError(msg % operator_name)
    return operator


def _compiler_add_child(obj, child):
    """ A compiler runtime function which add the child to the given 
    object.

    """
    obj.add_child(child)


def _compiler_add_children(obj, retval):
    """ A compiler runtime function which adds the return values of a
    call in an enaml body as children of the given object.

    """
    add_child = obj.add_child
    for item in retval:
        add_child(item)


def _compiler_eval(code, f_globals, f_locals):
    """ A compiler runtime function which evalues the given code object
    in the given globals and locals.

    """
    return eval(code, f_globals, f_locals)


#------------------------------------------------------------------------------
# Body Compiler
#------------------------------------------------------------------------------
class BodyCompiler(_NodeVisitor):
    """ A visitor which compiles the body of Declaration or Defn.

    """
    def __init__(self):
        self.ops = []
        self.identifiers = set()
    
    @classmethod
    def compile(cls, body_items):
        """ A classmethod that takes a list of Instantiation and Call 
        nodes and returns a list of code ops. The list of ops will expect
        a parent component to be at TOS.

        """
        compiler = cls()
        visit = compiler.visit
        for item in body_items:
            visit(item)
        return compiler.ops

    def visit_Instantiation(self, node):
        """ Create the bytecode ops for a component instantiation. The
        TOS should be a component instance which is the parent of the
        component being instantiated. The bytecode will not consume TOS.
        
        """
        bp = byteplay
        ops = self.ops

        # Duplicate TOS which is the parent of the component we are 
        # instantiating, this will be consumed at the end of this method.
        ops.append((bp.DUP_TOP, None))

        # Lookup the component type we are instantiating using the component
        # scope lookup callable, and call the __enaml_call__ method on the
        # returned component type. TOS will be an instance of that component.
        ops.extend([
            (bp.LOAD_NAME, node.name),
            (bp.LOAD_ATTR, '__enaml_call__'),
            (bp.CALL_FUNCTION, 0x0000),
        ])
        
        # If the instantiation is given an identifier, add the component
        # instance which is TOS to the identifier scope, keeping the instance 
        # on the TOS.
        idn = node.identifier
        identifiers = self.identifiers
        if idn is not None:
            if idn in identifiers:
                raise SyntaxError('Duplicate identifier `%s`' % idn)
            identifiers.add(idn)
            ops.extend([
                (bp.DUP_TOP, None),
                (bp.LOAD_NAME, '__store_id_scope__'),
                (bp.ROT_TWO, None),
                (bp.CALL_FUNCTION, 0x0001),
                (bp.POP_TOP, None),
            ])
        
        visit = self.visit
        for item in node.body:
            visit(item)
        
        # Once the children have finished compiling, we can add this 
        # instance as a child of the parent which was dup'd at the start
        # of this method. TOS is (..., parent, child).
        ops.extend([
            (bp.LOAD_CONST, _compiler_add_child),
            (bp.ROT_THREE, None),
            (bp.CALL_FUNCTION, 0x0002),
            (bp.POP_TOP, None),
        ])

    def visit_AttributeBinding(self, node):
        """ Create the bytecode ops for binding an expression to an 
        attribute. The TOS should be the component instance which has
        the attribute to which the expression is being bound. The code
        will not consume TOS.

        """
        # XXX handle BoundCodeBlock instead of just BoundExpression
        bp = byteplay
        ops = self.ops

        # Duplicate TOS which is the component to which we are binding 
        # the expression, this will be consumed during the method.
        ops.append((bp.DUP_TOP, None))

        # Compile the expression code object. This will be passed to the 
        # binding operator as an argument.
        expr_ast = node.binding.expr
        expr_code = compile(expr_ast, 'Enaml', model='eval')

        # A binding is accomplished by loading the appropriate binding
        # operator function and passing it the a number of arguments:
        # (obj, name, expr_ast, expr_code, globals_closure, locals_closure)
        ops.extend([
            (bp.LOAD_CONST, _compiler_load_operator),
            (bp.LOAD_CONST, node.binding.op),
            (bp.CALL_FUNCTION, 0x0001),
            (bp.ROT_TWO, None),
            (bp.LOAD_CONST, node.name),
            (bp.LOAD_CONST, expr_ast),
            (bp.LOAD_CONST, expr_code),
            (bp.LOAD_NAME, '__globals_closure__'),
            (bp.LOAD_NAME, '__locals_closure__'),
            (bp.CALL_FUNCTION, 0x0006),
            (bp.POP_TOP, None),
        ])

    def visit_Call(self, node):
        """ Create the bytecode ops for performing a call in the body
        of a declaration. The calls are expected to return iterables
        of children. The TOS should be parent to which these children
        are added. The code will not consume TOS.

        """
        bp = byteplay
        ops = self.ops

        # Duplicate TOS which is the parent of the component we are 
        # instantiating, this will be consumed at the end of this method.
        ops.append((bp.DUP_TOP, None))
        
        # To perform the call we need to load the callable and its args
        # and kwargs, call it, then use a compiler helper to handle the
        # return values.
        ops.append((bp.LOAD_NAME, node.name))
        n_args = 0
        n_kwargs = 0
        for arg in node.arguments:
            if isinstance(arg, enaml_ast.Argument):
                n_args += 1
            else:
                ops.append((bp.LOAD_CONST, arg.name))
                n_kwargs += 1
            arg_code = compile(arg.py_ast, 'Enaml', mode='eval')
            ops.extend([
                (bp.LOAD_CONST, _compiler_eval),
                (bp.LOAD_CONST, arg_code),
                (bp.LOAD_NAME, '__calling_globals__'),
                (bp.LOAD_NAME, '__calling_locals__'),
                (bp.CALL_FUNCTION, 0x0003),
            ])
        ops.extend([
            (bp.CALL_FUNCTION, (n_kwargs << 8) + n_args),
            (bp.LOAD_CONST, _compiler_add_children),
            (bp.ROT_THREE, None),
            (bp.CALL_FUNCTION, 0x0002),
            (bp.POP_TOP, None),
        ])
 

#------------------------------------------------------------------------------
# Enaml Declaration
#------------------------------------------------------------------------------
class EnamlDeclaration(object):
    """ An object which represents an enaml declaration. It manages
    building the appropriate customized type component type on-demand
    in an efficient manner.

    """
    def __init__(self, name, base_expr, module_dict, body_code):
        # A dictionary which maps the base type of the created type
        # to the actual created type. The mapping is needed because 
        # the base type may change under a different toolkit context.
        self._name = name
        self._created_types = {}
        self._base_expr = base_expr
        self._module_dict = module_dict
        self._body_code = body_code

    def __call__(self):
        """ Creates a new custom component type (if needed) and returns 
        a new instance of that type.

        """
        # Lookup the base type using the using a scope which is the 
        # union of the active toolkit and the module dict
        scope = {}
        scope.update(self._module_dict)
        scope.update(Toolkit.active_toolkit())

        try:
            base_type = eval(self._base_expr, scope)
        except NameError:
            msg = 'Unable to load base type for %s declaration' % self._name
            raise NameError(msg)
        
        # Make sure we have something valid from which to derive a new
        # component type. It's only possible to derive from subclasses of
        # BaseComponent, but the base may be retrieved from the toolkit
        # in the form of a Constructor.
        if isinstance(base_type, Constructor):
            base_type = base_type.shell_loader()

        if not issubclass(base_type, BaseComponent):
            msg = 'Cannot derive a new component type from `%s`' % base_type
            raise TypeError(msg)

        # If we've already created a type for this base component type,
        # then return an instance of that. Otherwise, create the new type
        # and return that.
        created = self._created_types
        if base_type in created:
            cmpnt_type = created[base_type]
        else:
            cmpnt_type = self._create_type(base_type, scope)
            created[base_type] = cmpnt_type

        instance = cmpnt_type()
        self._apply_var_defaults(instance, scope)

        return instance
    
    def _create_type(self, base_type, scope):
        """ Creates a new derived type for the given base type.

        """
        cls_name = self._name
        bases = (base_type,)

        # Compute the new class traits for the new declared attribute
        # variables.
        new_traits = []
        for var_decl in self._var_decls:
            var_type_code = compile(var_decl.type, 'Enaml', mode='eval')
            try:
                var_type = eval(var_type_code, scope)
            except NameError:
                msg = 'Cannot resolve var type for %s declaration'
                raise NameError(msg % self._name)
            
            if not isinstance(var_type, type):
                msg = 'Variable type `%s` is not a proper type' % var_type
                raise TypeError(msg)

            if var_type in _BUILTIN_TYPE_MAPPING:
                trait_type = _BUILTIN_TYPE_MAPPING[var_type]
            else:
                trait_type = t_types.Instance(var_type)
            
            for var in var_decl.vars:
                # We don't care about the default values at the moment,
                # since those are evaluated and applied each time a
                # instance of the new type is instantiated.
                new_traits.append((var.name, trait_type))

        cls_dict = dict(new_traits)

        return type(cls_name, bases, cls_dict)

    def _apply_var_defaults(self, instance, scope):
        """ Evaluates and applies the variable defaults for the given
        instance using the provided scope.

        """
        # XXX punting at the moment because I'm tired
        return
    
    def _create_children(self, instance, scope):
        """ Creates and adds the children to the given instance.

        """
        # XXX punting at the moment because I'm tired.
        return 


def build_declaration(node, module_dict):
    """ A function which takes a declaration node and the module dict in
    which it will live and builds a new class which implements the 
    declaration. The new class is added to the module dict.

    """
    # XXX punting at the moment because I'm tired.
    return 




