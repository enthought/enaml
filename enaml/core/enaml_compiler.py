#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import ast
import itertools

from .byteplay import (
    Code, LOAD_FAST, CALL_FUNCTION, LOAD_GLOBAL, STORE_FAST, LOAD_CONST,
    LOAD_ATTR, STORE_SUBSCR, RETURN_VALUE, POP_TOP, MAKE_FUNCTION,
    STORE_NAME, LOAD_NAME, SetLineno,
)


# Increment this number whenever the compiler changes the code which it
# generates. This number is used by the import hooks to know which version
# of a .enamlc file is valid for the Enaml compiler version in use. If 
# this number is not incremented on change, it may result in .enamlc
# files which fail on import.
#
# Version History
# ---------------
# 1 : Initial compiler version 2 February 2012
#
COMPILER_VERSION = 1


#------------------------------------------------------------------------------
# Compiler Helpers
#------------------------------------------------------------------------------
# Code that will be executed at the top of every enaml module
STARTUP = ['from enaml.core.factory import EnamlDeclaration']


# Cleanup code that will be included in every compiled enaml module
CLEANUP = ['del EnamlDeclaration']


def _var_name_generator():
    """ Returns a generator that generates sequential variable names for
    use in a code block.

    """
    count = itertools.count()
    while True:
        yield '_var_' + str(count.next())


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
        """ Compiles the given Declaration node into a byteplay code 
        object.

        Given this sample declaration in Enaml::
          
        FooWindow(Window):
            id: foo
            a = '12'
            PushButton:
                id: btn
                text = 'clickme'
        
        We generate bytecode that would correspond to a Python function that
        looks similar to this::
        
        def FooWindow(identifiers, toolkit):
            f_globals = globals()
            eval_ = eval
            foo_cls = eval('Window', toolkit, f_globals)
            foo = foo_cls.__enaml_call__(identifiers, toolkit)
            identifiers['foo'] = foo
            op = eval_('__operator_Equal__', toolkit, f_globals)
            op(foo, 'a', <ast>, <code>, identifiers, f_globals, toolkit)
            btn_cls = eval_('PushButton', toolkit, f_globals)
            btn = btn_cls.__enaml_call__(None, toolkit)
            identifiers['btn'] = button
            op = eval_('__operator_Equal__', toolkit, f_globals)
            op(item, 'text', <ast>, <code>, identifiers, f_globals, toolkit)
            foo.add_subcomponent(button)
            return foo
        
        """
        compiler = cls(filename)
        compiler.visit(node)
        code_ops = compiler.code_ops
        code = Code(
            code_ops, [], ['identifiers', 'toolkit'], False, False, True, 
            node.name, filename, node.lineno, node.doc,
        )
        return code

    def __init__(self, filename):
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
        """ Creates the bytecode ops for a declaration node. This visitor
        handles creating the component instance and storing it's identifer
        if one is given.

        """
        name = self.name_gen.next()
        extend_ops = self.extend_ops
        self.push_name(name)
        base_code = compile(node.base.py_ast, self.filename, mode='eval')
        extend_ops([
            # f_globals = globals()
            (LOAD_GLOBAL, 'globals'),
            (CALL_FUNCTION, 0x0000),
            (STORE_FAST, 'f_globals'),

            # eval_ = eval
            (LOAD_GLOBAL, 'eval'),
            (STORE_FAST, 'eval_'),

            # foo_cls = eval('Window', toolkit, f_globals)
            # foo = foo_cls.__enaml_call__(identifiers, toolkit)
            (LOAD_FAST, 'eval_'),
            (LOAD_CONST, base_code),
            (LOAD_FAST, 'toolkit'),
            (LOAD_FAST, 'f_globals'),
            (CALL_FUNCTION, 0x0003),
            (LOAD_ATTR, '__enaml_call__'),
            (LOAD_FAST, 'identifiers'),
            (LOAD_FAST, 'toolkit'),
            (CALL_FUNCTION, 0x0002),
            (STORE_FAST, name),
        ])

        if node.identifier:
            extend_ops([
                # identifiers['foo'] = foo
                (LOAD_FAST, name),
                (LOAD_FAST, 'identifiers'),
                (LOAD_CONST, node.identifier),
                (STORE_SUBSCR, None),
            ])
        
        visit = self.visit
        for item in node.body:
            visit(item)
        
        extend_ops([
            # return foo
            (LOAD_FAST, name),
            (RETURN_VALUE, None),
        ])

        self.pop_name()

    def visit_AttributeDeclaration(self, node):
        """ Creates the bytecode ops for an attribute declaration. This
        visitor handles adding a new attribute to a component.

        """
        extend_ops = self.extend_ops

        # Load the method that's going to be called and the
        # name of the attribute being declared.
        extend_ops([
            (LOAD_FAST, self.curr_name()),
            (LOAD_ATTR, 'add_attribute'),
            (LOAD_CONST, node.name),
        ])

        # Generate the ops to the load the type (if one was given),
        # and the call the add_attribute method
        node_type = node.type
        if node_type is not None:
            type_code = compile(node_type.py_ast, self.filename, mode='eval')
            extend_ops([
                (LOAD_FAST, 'eval_'),
                (LOAD_CONST, type_code),
                (LOAD_FAST, 'toolkit'),
                (LOAD_FAST, 'f_globals'),
                (CALL_FUNCTION, 0x0003),
                (LOAD_CONST, node.is_event),
                (CALL_FUNCTION, 0x0003),
                (POP_TOP, None),
            ])
        else:
            extend_ops([
                (LOAD_CONST, 'is_event'),
                (LOAD_CONST, node.is_event),
                (CALL_FUNCTION, 0x0101),
                (POP_TOP, None),
            ])

        # Visit the default attribute binding if one exists.
        default = node.default
        if default is not None:
            self.visit(node.default)

    def visit_AttributeBinding(self, node):
        """ Creates the bytecode ops for an attribute binding. This
        visitor handles loading and calling the appropriate operator.

        """
        # A binding is accomplished by loading the appropriate binding
        # operator function and passing it the a number of arguments:
        #
        # op = eval('__operator_Equal__', toolkit, f_globals)
        # op(item, 'a', code, identifiers, f_globals, toolkit)
        fn = self.filename
        op_code = compile(node.binding.op, fn, mode='eval')
        py_ast = node.binding.expr.py_ast
        if isinstance(py_ast, ast.Module):
            expr_code = compile(py_ast, fn, mode='exec')
        else:
            expr_code = compile(py_ast, fn, mode='eval')
        self.extend_ops([
            (LOAD_FAST, 'eval_'),
            (LOAD_CONST, op_code),
            (LOAD_FAST, 'toolkit'),
            (LOAD_FAST, 'f_globals'),
            (CALL_FUNCTION, 0x0003),
            (LOAD_FAST, self.curr_name()),
            (LOAD_CONST, node.name),
            (LOAD_CONST, expr_code),
            (LOAD_FAST, 'identifiers'),
            (LOAD_FAST, 'f_globals'),
            (LOAD_FAST, 'toolkit'),
            (CALL_FUNCTION, 0x0006),
            (POP_TOP, None),
        ])

    def visit_Instantiation(self, node):
        """ Create the bytecode ops for a component instantiation. This 
        visitor handles calling another derived component and storing
        its identifier, if given.
        
        """
        extend_ops = self.extend_ops
        name = self.name_gen.next()
        self.push_name(name)
        op_code = compile(node.name, self.filename, mode='eval')
        extend_ops([
            # btn_cls = eval('PushButton', toolkit, f_globals)
            # btn = btn_cls.__enaml_call__(None, toolkit)
            # When instantiating a Declaration, it is called without
            # identifiers, so that it creates it's own new identifiers
            # scope. This means that derived declarations share ids,
            # but the composed children have an isolated id space.
            (LOAD_FAST, 'eval_'),
            (LOAD_CONST, op_code),
            (LOAD_FAST, 'toolkit'),
            (LOAD_FAST, 'f_globals'),
            (CALL_FUNCTION, 0x0003),
            (LOAD_ATTR, '__enaml_call__'),
            (LOAD_CONST, None),
            (LOAD_FAST, 'toolkit'),
            (CALL_FUNCTION, 0x0002),
            (STORE_FAST, name),
        ])
        
        if node.identifier:
            extend_ops([
                (LOAD_FAST, name),
                (LOAD_FAST, 'identifiers'),
                (LOAD_CONST, node.identifier),
                (STORE_SUBSCR, None),
            ])

        visit = self.visit
        for item in node.body:
            visit(item)
        
        self.pop_name()
        extend_ops([
            # foo.add_subcomponent(button)
            (LOAD_FAST, self.curr_name()),
            (LOAD_ATTR, 'add_subcomponent'),
            (LOAD_FAST, name),
            (CALL_FUNCTION, 0x0001),
            (POP_TOP, None),
        ])


#------------------------------------------------------------------------------
# Enaml Compiler
#------------------------------------------------------------------------------
class EnamlCompiler(_NodeVisitor):
    """ A compiler that will compile an enaml module ast node.
    
    The entry point is the `compile` classmethod which will compile
    the ast into an appropriate python object and place the results 
    in the provided module dictionary.

    """
    @classmethod
    def compile(cls, module_ast, filename):
        """ The main entry point of the compiler.

        Parameters
        ----------
        module_ast : Instance(enaml_ast.Module)
            The enaml module ast node that should be compiled.
        
        module_dict : dict
            The dictionary of the Python module into which we are
            compiling the enaml code.
        
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
        self.code_ops = []
        self.filename = filename

    def visit_Module(self, node):
        """ The module node visitor method. Used internally by the
        compiler.

        """
        for item in node.body:
            self.visit(item)
    
    def visit_Python(self, node):
        """ A visitor which adds a chunk of raw Python into the module.

        """
        # This compiles the given Python ast into a Python code object
        # then disassembles it into a byteplay code object. This allows
        # us to interleave the instructions with those generated for
        # the rest of the module and then compile a single unified 
        # code object.
        py_code = compile(node.py_ast, self.filename, mode='exec')
        bpc = Code.from_code(py_code)
        # Skip the SetLineo and ReturnValue codes
        self.code_ops.extend(bpc.code[1:-2])

    def visit_Declaration(self, node):
        """ The declaration node visitor. This will add an instance
        of EnamlDeclaration to the module.

        """
        # This creates a function from the generated code ops then
        # wraps that function in an EnamlDeclaration.
        func_code = DeclarationCompiler.compile(node, self.filename)
        name = node.name
        self.code_ops.extend([
            (LOAD_CONST, func_code),
            (MAKE_FUNCTION, 0),
            (STORE_NAME, name),
            (LOAD_NAME, 'EnamlDeclaration'),
            (LOAD_NAME, name),
            (CALL_FUNCTION, 0x0001),
            (STORE_NAME, name),
        ])

