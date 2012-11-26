#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import ast
import itertools
import types

from .byteplay import (
    Code, LOAD_FAST, CALL_FUNCTION, LOAD_GLOBAL, STORE_FAST, LOAD_CONST,
    LOAD_ATTR, STORE_SUBSCR, RETURN_VALUE, POP_TOP, MAKE_FUNCTION, STORE_NAME,
    LOAD_NAME, DUP_TOP, SetLineno, BINARY_SUBSCR, STORE_ATTR, ROT_TWO
)
from .code_tracing import inject_tracing, inject_inversion


# Increment this number whenever the compiler changes the code which it
# generates. This number is used by the import hooks to know which version
# of a .enamlc file is valid for the Enaml compiler version in use. If
# this number is not incremented on change, it may result in .enamlc
# files which fail on import.
#
# Version History
# ---------------
# 1 : Initial compiler version - 2 February 2012
# 2 : Update line number handling - 26 March 2012
#     When compiling code objects with mode='eval', Python ignores the
#     line number specified by the ast. The workaround is to compile the
#     code object, then make a new copy of it with the proper firstlineno
#     set via the types.CodeType constructor.
# 3 : Update the generated code to remove the toolkit - 21 June 2012
#     This updates the compiler for the coming switch to async UI's
#     which will see the removal of the Toolkit concept. The only
#     magic scope maintained is for that of operators.
# 4 : Update component building - 27 July 2012
#     This updates the compiler to handle the new Enaml creation semantics
#     that don't rely on __enaml_call__. Instead the parent is passed
#     directly to the component cls which is a subclass of Declarative.
#     That class handles calling the builder functions upon instance
#     creation. This allows us to get rid of the EnamlDef class and
#     make enamldef constructs proper subclasses of Declarative.
# 5 : Change the import names - 28 July 2012
#     This changes the imported helper name from _make_decl_subclass_
#     to _make_enamldef_helper_ which is more descriptive, but equally
#     mangled. It also updates the method name used on the Declarative
#     component for adding attribute from _add_decl_attr to the more
#     descriptive _add_user_attribute. Finally, it adds the eval_compile
#     function for compiling Python code in 'eval' mode with proper line
#     number handling.
# 6 : Compile with code tracing - 24 November 2012
#     This updates the compiler to generate code using the idea of code
#     tracing instead of monitors and inverters. The compiler compiles
#     the expressions into functions which are augmented to accept
#     additional arguments. These arguments are tracer objects which will
#     have methods called in response to bytecode ops executing. These
#     methods can then attach listeners as necessary. This is an easier
#     paradigm to develop with than the previous incarnation. This new
#     way also allows the compiler to generate the final code objects
#     upfront, instead of needed to specialize at runtime for a given
#     operator context. This results in a much smaller footprint since
#     then number of code objects created is n instead of n x m.
COMPILER_VERSION = 6


# The Enaml compiler translates an Enaml AST into Python bytecode.
#
# Given this sample declaration in Enaml::
#
# FooWindow(Window):
#     id: foo
#     a = '12'
#     PushButton:
#         id: btn
#         text = 'clickme'
#
# The compiler generate bytecode that would corresponds to the following
# Python code (though the function object is never assigned to a name in
# the global namespace).
#
# def FooWindow(instance, identifiers, operators):
#     f_globals = globals()
#     _var_1 = instance
#     identifiers['foo'] = _var_1
#     op = operators['__operator_Equal__']
#     op(_var_1, 'a', <function>, identifiers)
#     _var_2 = f_globals['PushButton'](_var_1)
#     identifiers['btn'] = _var_2
#     op = operators['__operator_Equal__']
#     op(_var_2, 'text', <function>, identifiers)
#     return _var_1
#
# FooWindow = _make_enamldef_helper_('FooWindow', Window, FooWindow)


#------------------------------------------------------------------------------
# Compiler Helpers
#------------------------------------------------------------------------------
# Code that will be executed at the top of every enaml module
STARTUP = ['from enaml.core.compiler_helpers import _make_enamldef_helper_']


# Cleanup code that will be included in every compiled enaml module
CLEANUP = ['del _make_enamldef_helper_']


def _var_name_generator():
    """ Returns a generator that generates sequential variable names for
    use in a code block.

    """
    count = itertools.count()
    while True:
        yield '_var_' + str(count.next())


def update_firstlineno(code, firstlineno):
    """ Returns a new code object with an updated first line number.

    """
    return types.CodeType(
        code.co_argcount, code.co_nlocals, code.co_stacksize, code.co_flags,
        code.co_code, code.co_consts, code.co_names, code.co_varnames,
        code.co_filename, code.co_name, firstlineno, code.co_lnotab,
        code.co_freevars, code.co_cellvars,
    )


#------------------------------------------------------------------------------
# Expression Compilers
#------------------------------------------------------------------------------
def replace_global_loads(codelist, explicit=None):
    """ A code transformer which rewrites LOAD_GLOBAL opcodes.

    This transform will replace the LOAD_GLOBAL opcodes with LOAD_NAME
    opcodes. The operation is performed in-place.

    Parameters
    ----------
    codelist : list
        The list of byteplay code ops to modify.

    explicit : set or None
        The set of global names declared explicitly and which should
        remain untransformed.

    """
    # Replacing LOAD_GLOBAL with LOAD_NAME enables dynamic scoping by
    # way of a custom locals mapping. The `call_func` function in the
    # `funchelper` module enables passing a locals map to a function.
    explicit = explicit or set()
    for idx, (op, op_arg) in enumerate(codelist):
        if op == LOAD_GLOBAL and op_arg not in explicit:
            codelist[idx] = (LOAD_NAME, op_arg)


def optimize_locals(codelist):
    """ Optimize the given code object for fast locals access.

    All STORE_NAME opcodes will be replaced with STORE_FAST. Names which
    are stored and then loaded via LOAD_NAME are rewritten to LOAD_FAST.
    This transformation is applied in-place.

    Parameters
    ----------
    codelist : list
        The list of byteplay code ops to modify.

    """
    fast_locals = set()
    for idx, (op, op_arg) in enumerate(codelist):
        if op == STORE_NAME:
            fast_locals.add(op_arg)
            codelist[idx] = (STORE_FAST, op_arg)
    for idx, (op, op_arg) in enumerate(codelist):
        if op == LOAD_NAME and op_arg in fast_locals:
            codelist[idx] = (LOAD_FAST, op_arg)


def compile_simple(py_ast, filename):
    """ Compile an ast into a code object implementing operator `=`.

    Parameters
    ----------
    py_ast : ast.Expression
        A Python ast Expression node.

    filename : str
        The filename which generated the expression.

    Returns
    -------
    result : types.CodeType
        A Python code object which implements the desired behavior.

    """
    code = compile(py_ast, filename, mode='eval')
    code = update_firstlineno(code, py_ast.lineno)
    bp_code = Code.from_code(code)
    replace_global_loads(bp_code.code)
    optimize_locals(bp_code.code)
    bp_code.newlocals = False
    return bp_code.to_code()


def compile_notify(py_ast, filename):
    """ Compile an ast into a code object implementing operator `::`.

    Parameters
    ----------
    py_ast : ast.Module
        A Python ast Module node.

    filename : str
        The filename which generated the expression.

    Returns
    -------
    result : types.CodeType
        A Python code object which implements the desired behavior.

    """
    explicit_globals = set()
    for node in ast.walk(py_ast):
        if isinstance(node, ast.Global):
            explicit_globals.update(node.names)
    code = compile(py_ast, filename, mode='exec')
    bp_code = Code.from_code(code)
    replace_global_loads(bp_code.code, explicit_globals)
    optimize_locals(bp_code.code)
    bp_code.newlocals = False
    return bp_code.to_code()


def compile_subscribe(py_ast, filename):
    """ Compile an ast into a code object implementing operator `<<`.

    Parameters
    ----------
    py_ast : ast.Expression
        A Python ast Expression node.

    filename : str
        The filename which generated the expression.

    Returns
    -------
    result : types.CodeType
        A Python code object which implements the desired behavior.

    """
    code = compile(py_ast, filename, mode='eval')
    code = update_firstlineno(code, py_ast.lineno)
    bp_code = Code.from_code(code)
    replace_global_loads(bp_code.code)
    optimize_locals(bp_code.code)
    bp_code.code = inject_tracing(bp_code.code)
    bp_code.newlocals = False
    bp_code.args = ('_[tracer]',) + bp_code.args
    return bp_code.to_code()


def compile_update(py_ast, filename):
    """ Compile an ast into a code object implementing operator `>>`.

    Parameters
    ----------
    py_ast : ast.Expression
        A Python ast Expression node.

    filename : str
        The filename which generated the expression.

    Returns
    -------
    result : types.CodeType
        A Python code object which implements the desired behavior.

    """
    code = compile(py_ast, filename, mode='eval')
    code = update_firstlineno(code, py_ast.lineno)
    bp_code = Code.from_code(code)
    replace_global_loads(bp_code.code)
    optimize_locals(bp_code.code)
    bp_code.code = inject_inversion(bp_code.code)
    bp_code.newlocals = False
    bp_code.args = ('_[inverter]', '_[value]') + bp_code.args
    return bp_code.to_code()


def compile_delegate(py_ast, filename):
    """ Compile an ast into a code object implementing operator `:=`.

    This will generate two code objects: one which is equivalent to
    operator `<<` and another which is equivalent to `>>`.

    Parameters
    ----------
    py_ast : ast.Expression
        A Python ast Expression node.

    filename : str
        The filename which generated the expression.

    Returns
    -------
    result : tuple
        A 2-tuple of types.CodeType equivalent to operators `<<` and
        `>>` respectively.

    """
    code = compile(py_ast, filename, mode='eval')
    code = update_firstlineno(code, py_ast.lineno)
    bp_code = Code.from_code(code)
    bp_code.newlocals = False
    codelist = bp_code.code[:]
    bp_args = tuple(bp_code.args)
    replace_global_loads(codelist)
    optimize_locals(codelist)
    sub_list = inject_tracing(codelist)
    bp_code.code = sub_list
    bp_code.args = ('_[tracer]',) + bp_args
    sub_code = bp_code.to_code()
    upd_list = inject_inversion(codelist)
    bp_code.code = upd_list
    bp_code.args = ('_[inverter]', '_[value]') + bp_args
    upd_code = bp_code.to_code()
    return (sub_code, upd_code)


COMPILE_OP_MAP = {
    '__operator_Equal__': compile_simple,
    '__operator_ColonColon__': compile_notify,
    '__operator_LessLess__': compile_subscribe,
    '__operator_GreaterGreater__': compile_update,
    '__operator_ColonEqual__': compile_delegate,
}


#------------------------------------------------------------------------------
# Node Visitor
#------------------------------------------------------------------------------
class _NodeVisitor(object):
    """ A node visitor class that is used as base class for the various
    Enaml compilers.

    """
    def visit(self, node):
        """ The main visitor dispatch method.

        Unhandled nodes will raise an error.

        """
        name = 'visit_%s' % node.__class__.__name__
        try:
            method = getattr(self, name)
        except AttributeError:
            method = self.default_visit
        method(node)

    def visit_nonstrict(self, node):
        """ A nonstrict visitor dispatch method.

        Unhandled nodes will be ignored.

        """
        name = 'visit_%s' % node.__class__.__name__
        try:
            method = getattr(self, name)
        except AttributeError:
            pass
        else:
            method(node)

    def default_visit(self, node):
        """ The default visitor method. Raises an error since there
        should not be any unhandled nodes.

        """
        raise ValueError('Unhandled Node %s.' % node)


#------------------------------------------------------------------------------
# Declaration Compiler
#------------------------------------------------------------------------------
class DeclarationCompiler(_NodeVisitor):
    """ A visitor which compiles a Declaration node into a code object.

    """
    @classmethod
    def compile(cls, node, filename):
        """ The main entry point of the DeclarationCompiler.

        This compiler compiles the given Declaration node into a code
        object for a builder function.

        Parameters
        ----------
        node : Declaration
            The Declaration node to compiler.

        filename : str
            The string filename to use for the generated code objects.

        """
        compiler = cls(filename)
        compiler.visit(node)
        code_ops = compiler.code_ops
        code = Code(
            code_ops, [], ['instance', 'identifiers', 'operators'], False,
            False, True, node.name, filename, node.lineno, node.doc,
        )
        return code

    def __init__(self, filename):
        """ Initialize a DeclarationCompiler.

        Parameters
        ----------
        filename : str
            The filename string to use for the generated code object.

        """
        self.filename = filename
        self.code_ops = []
        self.extend_ops = self.code_ops.extend
        self.name_gen = _var_name_generator()
        self.name_stack = []
        self.push_name = self.name_stack.append
        self.pop_name = self.name_stack.pop

    def curr_name(self):
        """ Returns the current variable name on the stack.

        """
        return self.name_stack[-1]

    def visit_Declaration(self, node):
        """ Creates the bytecode ops for a declaration node.

        This node visitor pulls the passed in root into a local var
        and stores it's identifier if one is given. It also loads
        in the commonly used local variables `f_globals`, and `eval_`.

        """
        name = self.name_gen.next()
        extend_ops = self.extend_ops
        self.push_name(name)

        extend_ops([
            (LOAD_NAME, 'globals'),     # f_globals = globals()
            (CALL_FUNCTION, 0x0000),
            (STORE_FAST, 'f_globals'),
            (LOAD_FAST, 'instance'),    # _var_1 = instance
            (STORE_FAST, name),
        ])

        if node.identifier:
            extend_ops([
                (LOAD_FAST, name),              # identifiers['foo'] = _var_1
                (LOAD_FAST, 'identifiers'),
                (LOAD_CONST, node.identifier),
                (STORE_SUBSCR, None),
            ])

        visit = self.visit
        for item in node.body:
            visit(item)

        extend_ops([
            (LOAD_FAST, name),      # return _var_1
            (RETURN_VALUE, None),
        ])

        self.pop_name()

    def visit_AttributeDeclaration(self, node):
        """ Creates the bytecode ops for an attribute declaration.

        The attributes will have already been added to the subclass, so
        this visitor just dispatches to any default bindings which may
        exist on the attribute declaration, since the binding happens
        at instantiation time via operators.

        """
        default = node.default
        if default is not None:
            self.visit(node.default)

    def visit_AttributeBinding(self, node):
        """ Creates the bytecode ops for an attribute binding.

        This visitor handles loading and calling the appropriate
        operator.

        """
        py_ast = node.binding.expr.py_ast
        op = node.binding.op
        op_compiler = COMPILE_OP_MAP[op]
        code = op_compiler(py_ast, self.filename)
        if isinstance(code, tuple): # operator `::`
            sub_code, upd_code = code
            self.extend_ops([
                (SetLineno, node.binding.lineno),
                (LOAD_FAST, 'operators'),           # operators[op](obj, attr, sub_func, identifiers)
                (LOAD_CONST, op),
                (BINARY_SUBSCR, None),
                (LOAD_FAST, self.curr_name()),
                (LOAD_CONST, node.name),
                (LOAD_CONST, sub_code),
                (MAKE_FUNCTION, 0),
                (DUP_TOP, None),
                (LOAD_CONST, upd_code),
                (MAKE_FUNCTION, 0),
                (ROT_TWO, None),
                (STORE_ATTR, '_update'),            # sub_func._update = upd_func
                (LOAD_FAST, 'identifiers'),
                (CALL_FUNCTION, 0x0004),
                (POP_TOP, None),
            ])
        else:
            self.extend_ops([
                (SetLineno, node.binding.lineno),
                (LOAD_FAST, 'operators'),           # operators[op](obj, attr, func, identifiers)
                (LOAD_CONST, op),
                (BINARY_SUBSCR, None),
                (LOAD_FAST, self.curr_name()),
                (LOAD_CONST, node.name),
                (LOAD_CONST, code),
                (MAKE_FUNCTION, 0),
                (LOAD_FAST, 'identifiers'),
                (CALL_FUNCTION, 0x0004),
                (POP_TOP, None),
            ])

    def visit_Instantiation(self, node):
        """ Create the bytecode ops for a component instantiation.

        This visitor handles calling another derived component and
        storing its identifier, if given.

        """
        extend_ops = self.extend_ops
        parent_name = self.curr_name()
        name = self.name_gen.next()
        self.push_name(name)
        extend_ops([
            (SetLineno, node.lineno),
            (LOAD_NAME, node.name),     # _var_2 = globals()['PushButton'](parent)
            (LOAD_FAST, parent_name),
            (CALL_FUNCTION, 0x0001),
            (STORE_FAST, name),
        ])

        if node.identifier:
            extend_ops([
                (LOAD_FAST, name),              # identifiers['btn'] = _var_2
                (LOAD_FAST, 'identifiers'),
                (LOAD_CONST, node.identifier),
                (STORE_SUBSCR, None),
            ])

        visit = self.visit
        for item in node.body:
            visit(item)

        self.pop_name()


#------------------------------------------------------------------------------
# Enaml Compiler
#------------------------------------------------------------------------------
class EnamlCompiler(_NodeVisitor):
    """ A visitor that will compile an enaml module ast node.

    The entry point is the `compile` classmethod which will compile
    the ast into an appropriate python code object for a module.

    """
    @classmethod
    def compile(cls, module_ast, filename):
        """ The main entry point of the compiler.

        Parameters
        ----------
        module_ast : Instance(enaml_ast.Module)
            The enaml module ast node that should be compiled.

        filename : str
            The string filename of the module ast being compiled.

        """
        compiler = cls(filename)
        compiler.visit(module_ast)

        module_ops = [(SetLineno, 1)]
        extend_ops = module_ops.extend

        # Generate the startup code for the module
        for start in STARTUP:
            start_code = compile(start, filename, mode='exec')
            # Skip the SetLineo and ReturnValue codes
            extend_ops(Code.from_code(start_code).code[1:-2])

        # Add in the code ops for the module
        extend_ops(compiler.code_ops)

        # Generate the cleanup code for the module
        for end in CLEANUP:
            end_code = compile(end, filename, mode='exec')
            # Skip the SetLineo and ReturnValue codes
            extend_ops(Code.from_code(end_code).code[1:-2])

        # Add in the final return value ops
        extend_ops([
            (LOAD_CONST, None),
            (RETURN_VALUE, None),
        ])

        # Generate and return the module code object.
        mod_code = Code(
            module_ops, [], [], False, False, False, '',  filename, 0, '',
        )
        return mod_code.to_code()

    def __init__(self, filename):
        """ Initialize an EnamlCompiler.

        Parameters
        ----------
        filename : str
            The string filename of the module ast being compiled.

        """
        self.filename = filename
        self.code_ops = []
        self.extend_ops = self.code_ops.extend

    def visit_Module(self, node):
        """ The Module node visitor method.

        This visitor dispatches to all of the body nodes of the module.

        """
        visit = self.visit
        for item in node.body:
            visit(item)

    def visit_Python(self, node):
        """ The Python node visitor method.

        This visitor adds a chunk of raw Python into the module.

        """
        py_code = compile(node.py_ast, self.filename, mode='exec')
        bp_code = Code.from_code(py_code)
        # Skip the SetLineo and ReturnValue codes
        self.extend_ops(bp_code.code[1:-2])

    def visit_Declaration(self, node):
        """ The Declaration node visitor.

        This generates the bytecode ops whic create a new type for the
        enamldef and then adds the user defined attributes and events.
        It also dispatches to the DeclarationCompiler which will create
        the builder function for the new type.

        """
        name = node.name
        extend_ops = self.extend_ops
        filename = self.filename
        func_code = DeclarationCompiler.compile(node, filename)
        extend_ops([
            (SetLineno, node.lineno),
            (LOAD_NAME, '_make_enamldef_helper_'),  # Foo = _make_enamldef_helper_(name, base, buildfunc)
            (LOAD_CONST, name),
            (LOAD_NAME, node.base),
            (LOAD_CONST, func_code),
            (MAKE_FUNCTION, 0),
            (CALL_FUNCTION, 0x0003),
            (STORE_NAME, name),
        ])

        # We now have a new Declarative subclass stored at 'name' to
        # which we need to add any user defined attributes and events.
        extend_ops([
            (LOAD_NAME, name),
            (LOAD_ATTR, '_add_user_attribute'),
        ])

        # Dispatch to add any class-level info contained within the
        # declaration body. Visit nonstrict since not all child nodes
        # are valid at the class-level. The '_add_user_attribute'
        # class method is left on the top of the stack and popped
        # at the end of the visitors.
        visit = self.visit_nonstrict
        for child_node in node.body:
            visit(child_node)

        extend_ops([(POP_TOP, None)])

    def visit_AttributeDeclaration(self, node):
        """ Creates the bytecode ops for an attribute declaration.

        This will add the ops to add the user attrs and events to
        the new type.

        """
        attr_type = node.type or 'object'
        self.extend_ops([
            (SetLineno, node.lineno),
            (DUP_TOP, None),                #cls._add_user_attribute(name, type, is_event)
            (LOAD_CONST, node.name),
            (LOAD_NAME, attr_type),
            (LOAD_CONST, node.is_event),
            (CALL_FUNCTION, 0x0003),
            (POP_TOP, None),
        ])

