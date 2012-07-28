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
COMPILER_VERSION = 4


#------------------------------------------------------------------------------
# Compiler Helpers
#------------------------------------------------------------------------------
# Code that will be executed at the top of every enaml module
STARTUP = ['from enaml.core.compiler_helpers import _make_decl_subclass']


# Cleanup code that will be included in every compiled enaml module
CLEANUP = ['del _make_decl_subclass']


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
        
        def FooWindow(instance, identifiers, operators):
            f_globals = globals()
            eval_ = eval
            identifiers['foo'] = instance
            op = eval_('__operator_Equal__', operators)
            op(foo, 'a', <ast>, <code>, identifiers, f_globals, operators)
            btn_cls = eval_('PushButton', f_globals)
            btn = btn_cls(foo)
            identifiers['btn'] = button
            op = eval_('__operator_Equal__', operators)
            op(item, 'text', <ast>, <code>, identifiers, f_globals, operators)
            return foo
        
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
        in commonly used local variables f_globals, and eval_.

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

            # foo_cls = root
            (LOAD_FAST, 'instance'),
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
        """ Creates the bytecode ops for an attribute declaration. 

        The attributes will have already been added to the subclass, so
        this visitor just dispatches to any default bindings which may
        exist on the attribute declaration.

        """
        # Visit the default attribute binding if one exists.
        default = node.default
        if default is not None:
            self.visit(node.default)

    def visit_AttributeBinding(self, node):
        """ Creates the bytecode ops for an attribute binding. 

        This visitor handles loading and calling the appropriate operator.

        """
        # A binding is accomplished by loading the appropriate binding
        # operator function and passing it the operator arguments:
        #
        # op = eval('__operator_Equal__', operators)
        # op(item, 'a', code, identifiers, f_globals, operators)
        fn = self.filename
        op_code = compile(node.binding.op, fn, mode='eval')
        op_code = update_firstlineno(op_code, node.binding.lineno)
        py_ast = node.binding.expr.py_ast
        if isinstance(py_ast, ast.Module):
            expr_code = compile(py_ast, fn, mode='exec')
        else:
            # When compiling in 'eval' mode, the line number in the ast
            # gets ignored. We need to make new code object from this
            # one with the proper starting line number so that 
            # exceptions are properly reported.
            expr_code = compile(py_ast, fn, mode='eval')
            expr_code = update_firstlineno(expr_code, py_ast.lineno)
        self.extend_ops([
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
        """ Create the bytecode ops for a component instantiation. This 
        visitor handles calling another derived component and storing
        its identifier, if given.
        
        """
        extend_ops = self.extend_ops
        parent_name = self.curr_name()
        name = self.name_gen.next()
        self.push_name(name)
        op_code = compile(node.name, self.filename, mode='eval')
        # Line numbers are ignored when compiling in 'eval' mode.
        # This restores the line number information.
        op_code = update_firstlineno(op_code, node.lineno)
        extend_ops([
            # btn_cls = eval('PushButton', f_globals)
            # btn = btn_cls.(parent)
            # When instantiating a Declaration, it is called without
            # identifiers, so that it creates it's own new identifiers
            # scope. This means that derived declarations share ids,
            # but the composed children have an isolated id namespace.
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
        of EnamlDef to the module.

        """
        name = node.name
        extend_ops = self.code_ops.extend

        func_code = DeclarationCompiler.compile(node, self.filename)
        base_code = compile(node.base.py_ast, self.filename, mode='eval')
        # Line numbers are ignored when compiling in 'eval' mode.
        # This restores the line number information.
        base_code = update_firstlineno(base_code, node.base.lineno)

        self.code_ops.extend([
            (SetLineno, node.lineno),
            (LOAD_NAME, '_make_decl_subclass'),
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

        # We now have a new Declarative subclass stored at name, which 
        # we need to use to add the new class attributes.
        extend_ops([
            (LOAD_NAME, name),
            (LOAD_ATTR, '_add_decl_attr'),
        ])

        # This loop adds the ops to add the attributes to the new subclass
        for child_node in node.body:
            if type(child_node).__name__ == 'AttributeDeclaration':
                extend_ops([
                    (SetLineno, child_node.lineno),
                    (DUP_TOP, None),
                    (LOAD_CONST, child_node.name),
                ])
                attr_type = child_node.type
                if attr_type is not None:
                    attr_type_code = compile(
                        attr_type.py_ast, self.filename, mode='eval'
                    )
                    attr_type_code = update_firstlineno(
                        attr_type_code, attr_type.lineno
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

