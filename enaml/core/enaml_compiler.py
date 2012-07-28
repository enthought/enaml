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
    LOAD_NAME, DUP_TOP, SetLineno,
)


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
COMPILER_VERSION = 5


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
#     eval_ = eval
#     _var_1 = instance
#     identifiers['foo'] = _var_1
#     op = eval_('__operator_Equal__', operators)
#     op(_var_1, 'a', <code for '12'>, identifiers, f_globals, operators)
#     _var_2 = eval_('PushButton', f_globals)(_var_1)
#     identifiers['btn'] = _var_2
#     op = eval_('__operator_Equal__', operators)
#     op(_var_2, 'text', <code for 'clickme'>, identifiers, f_globals, operators)
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


def eval_compile(item, filename, lineno):
    """ Compile the item in eval mode, updating the lineno as necessary.

    Parameters
    ----------
    item : string or ast
        A string of Python code, or a Python AST object.

    filename : string
        The string filename to use when compiling.

    lineno : int
        The line number to use for the returned code object.

    """
    code = compile(item, filename, mode='eval')
    return update_firstlineno(code, lineno)


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
        in the commonly used local variables f_globals, and eval_.

        """
        name = self.name_gen.next()
        extend_ops = self.extend_ops
        self.push_name(name)

        extend_ops([
            # f_globals = globals()
            (LOAD_GLOBAL, 'globals'),
            (CALL_FUNCTION, 0x0000),
            (STORE_FAST, 'f_globals'),
            # eval_ = eval
            (LOAD_GLOBAL, 'eval'),
            (STORE_FAST, 'eval_'),
            # _var_1 = instance
            (LOAD_FAST, 'instance'),
            (STORE_FAST, name),
        ])

        if node.identifier:
            extend_ops([
                # identifiers['foo'] = _var_1
                (LOAD_FAST, name),
                (LOAD_FAST, 'identifiers'),
                (LOAD_CONST, node.identifier),
                (STORE_SUBSCR, None),
            ])
        
        visit = self.visit
        for item in node.body:
            visit(item)
        
        extend_ops([
            # return _var_1
            (LOAD_FAST, name),
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
        fn = self.filename
        op_code = eval_compile(node.binding.op, fn, node.binding.lineno)
        py_ast = node.binding.expr.py_ast
        if isinstance(py_ast, ast.Module):
            expr_code = compile(py_ast, fn, mode='exec')
        else:
            expr_code = eval_compile(py_ast, fn, py_ast.lineno)
        self.extend_ops([
            # op = eval('__operator_Equal__', operators)
            # op(item, 'a', code, identifiers, f_globals, operators)
            (LOAD_FAST, 'eval_'),
            (LOAD_CONST, op_code),
            (LOAD_FAST, 'operators'),
            (CALL_FUNCTION, 0x0002),
            (LOAD_FAST, self.curr_name()),
            (LOAD_CONST, node.name),
            (LOAD_CONST, expr_code),
            (LOAD_FAST, 'identifiers'),
            (LOAD_FAST, 'f_globals'),
            (LOAD_FAST, 'operators'),
            (CALL_FUNCTION, 0x0006),
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
        op_code = eval_compile(node.name, self.filename, node.lineno)
        extend_ops([
            # _var_2 = eval('PushButton', f_globals)(parent)
            (LOAD_FAST, 'eval_'),
            (LOAD_CONST, op_code),
            (LOAD_FAST, 'f_globals'),
            (CALL_FUNCTION, 0x0002),
            (LOAD_FAST, parent_name),
            (CALL_FUNCTION, 0x0001),
            (STORE_FAST, name),
        ])
        
        if node.identifier:
            extend_ops([
                # identifiers['btn'] = _var_2
                (LOAD_FAST, name),
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
        for item in node.body:
            self.visit(item)
    
    def visit_Python(self, node):
        """ The Python node visitor method.
        
        This visitor adds a chunk of raw Python into the module.

        """
        py_code = compile(node.py_ast, self.filename, mode='exec')
        bpc = Code.from_code(py_code)
        # Skip the SetLineo and ReturnValue codes
        self.extend_ops(bpc.code[1:-2])

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
        base_code = eval_compile(node.base.py_ast, filename, node.base.lineno)

        extend_ops([
            (SetLineno, node.lineno),
            (LOAD_NAME, '_make_enamldef_helper_'),
            (LOAD_CONST, name),
            (LOAD_NAME, 'eval'),
            (LOAD_CONST, base_code),
            (LOAD_NAME, 'globals'),
            (CALL_FUNCTION, 0x0000),
            (CALL_FUNCTION, 0x0002),
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

        # This loop adds the ops to add the user attrs and events.
        for child_node in node.body:
            if type(child_node).__name__ == 'AttributeDeclaration':
                extend_ops([
                    (SetLineno, child_node.lineno),
                    (DUP_TOP, None),
                    (LOAD_CONST, child_node.name),
                ])
                attr_type = child_node.type
                if attr_type is not None:
                    attr_type_code = eval_compile(
                        attr_type.py_ast, filename, attr_type.lineno
                    )
                    extend_ops([
                        (LOAD_NAME, 'eval'),
                        (LOAD_CONST, attr_type_code),
                        (LOAD_NAME, 'globals'),
                        (CALL_FUNCTION, 0x0000),
                        (CALL_FUNCTION, 0x0002),
                        (LOAD_CONST, child_node.is_event),
                        (CALL_FUNCTION, 0x0003),
                        (POP_TOP, None),
                    ])
                else:
                    extend_ops([
                        (LOAD_NAME, 'object'),
                        (LOAD_CONST, child_node.is_event),
                        (CALL_FUNCTION, 0x0003),
                        (POP_TOP, None),
                    ])

        extend_ops([(POP_TOP, None)])

