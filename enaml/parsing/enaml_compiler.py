#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import itertools
from functools import wraps
import types

from . import byteplay

from .. import imports
from ..toolkit import Toolkit


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
# Compiler Helpers
#------------------------------------------------------------------------------
def _var_name_generator():
    """ Returns a generator that generates sequential variable names for
    use in a code block.

    """
    count = itertools.count()
    while True:
        yield '_var_' + str(count.next())


def _decl_wrapper_gen(func):
    """ Wraps a generated declaration function in a wrapper which creates
    the identifier scope if necessary, and loads the active toolkit if
    necessary.

    """
    @wraps(func)
    def wrapper(identifiers=None, toolkit=None):
        if identifiers is None:
            identifiers = {}
        if toolkit is None:
            toolkit = Toolkit.active_toolkit()
        return func(identifiers, toolkit)
    return wrapper


#------------------------------------------------------------------------------
# Declaration Compiler
#------------------------------------------------------------------------------
class DeclarationCompiler(_NodeVisitor):
    """ A visitor which compiles a Declaration node into a code object.

    """
    def __init__(self):
        self.ops = []
        self.name_gen = _var_name_generator()
        self.name_stack = []

    @classmethod
    def compile(cls, node):
        """ Compiles the given Declaration node into a code object.

        Given this sample declaration:
          
            FooWindow(Window) foo:
                a = '12'
                PushButton button:
                    text = 'clickme'
        
        We generate bytecode that would correspond to a function that 
        looks similar to this:
        
            def FooWindow(identifiers, toolkit):
                f_globals = globals()
                foo = eval('Window', toolkit, f_globals)(identifiers, 
                                                         toolkit)
                identifiers['foo'] = foo
                op = eval('__operator_Equal__', toolkit, f_globals)
                op(foo, 'a', <ast for '12'>, <code for '12'>, 
                   f_globals, identifiers)
                button = eval('PushButton', toolkit, f_globals)(identifiers, 
                                                                toolkit)
                identifiers['button'] = button
                op = eval('__operator_Equal__', toolkit, f_globals)
                op(item, 'text', <ast for 'clickme'>, <code for 'clickme'>, 
                   f_globals, identifiers)
                foo._subcomponents.append(button)
                return foo
        
        """
        compiler = cls()
        compiler.visit(node)
        ops = compiler.ops
        code = byteplay.Code(ops, [], ['identifiers', 'toolkit'], False, False,
                             True, node.name, 'Enaml', node.lineno, node.doc)
        return code.to_code()

    def visit_Declaration(self, node):
        """ Creates the bytecode ops for a declaration node. This visitor
        handles creating the component instance and storing it's identifer
        if one is given.

        """
        bp = byteplay
        ops = self.ops
        name_stack = self.name_stack

        name = self.name_gen.next()
        name_stack.append(name)
        ops.extend([
            # f_globals = globals()
            (bp.LOAD_GLOBAL, 'globals'),
            (bp.CALL_FUNCTION, 0x0000),
            (bp.STORE_FAST, 'f_globals'),

            # foo = eval('Window', toolkit, f_globals)(identifiers, toolkit)
            (bp.LOAD_CONST, eval),
            (bp.LOAD_CONST, node.base.code),
            (bp.LOAD_FAST, 'toolkit'),
            (bp.LOAD_FAST, 'f_globals'),
            (bp.CALL_FUNCTION, 0x0003),
            (bp.LOAD_FAST, 'identifiers'),
            (bp.LOAD_FAST, 'toolkit'),
            (bp.CALL_FUNCTION, 0x0002),
            (bp.STORE_FAST, name),
        ])

        if node.identifier:
            ops.extend([
                # identifiers['foo'] = foo
                (bp.LOAD_FAST, name),
                (bp.LOAD_FAST, 'identifiers'),
                (bp.LOAD_CONST, node.identifier),
                (bp.STORE_SUBSCR, None),
            ])

        for item in node.body:
            self.visit(item)
        
        ops.extend([
            # return foo
            (bp.LOAD_FAST, name),
            (bp.RETURN_VALUE, None),
        ])

        name_stack.pop()

    def visit_AttributeBinding(self, node):
        """ Creates the bytecode ops for an attribute binding. This
        visitor handles loading and calling the appropriate operator.

        """
        # XXX handle BoundCodeBlock instead of just BoundExpression
        bp = byteplay
        ops = self.ops
        name_stack = self.name_stack

        # Grab the ast and code object for the expression. These will
        # be passed to the binding operator.
        expr_ast = node.binding.expr.py_ast
        expr_code = node.binding.expr.code
        op_code = compile(node.binding.op, 'Enaml', mode='eval')

        # A binding is accomplished by loading the appropriate binding
        # operator function and passing it the a number of arguments:
        #
        # op = eval('__operator_Equal__', toolkit, f_globals)
        # op(item, 'a', <ast>, <code>, f_globals, toolkit, identifiers)
        ops.extend([
            (bp.LOAD_CONST, eval),
            (bp.LOAD_CONST, op_code),
            (bp.LOAD_FAST, 'toolkit'),
            (bp.LOAD_FAST, 'f_globals'),
            (bp.CALL_FUNCTION, 0x0003),
            (bp.LOAD_FAST, name_stack[-1]),
            (bp.LOAD_CONST, node.name),
            (bp.LOAD_CONST, expr_ast),
            (bp.LOAD_CONST, expr_code),
            (bp.LOAD_FAST, 'f_globals'),
            (bp.LOAD_FAST, 'toolkit'),
            (bp.LOAD_FAST, 'identifiers'),
            (bp.CALL_FUNCTION, 0x0007),
            (bp.POP_TOP, None),
        ])

    def visit_Instantiation(self, node):
        """ Create the bytecode ops for a component instantiation. This 
        visitor handles calling another derived component and storing
        its identifier, if given.
        
        """
        bp = byteplay
        ops = self.ops
        name_stack = self.name_stack

        # This is similar logic to visit_Declaration
        name = self.name_gen.next()
        name_stack.append(name)

        op_code = compile(node.name, 'Enaml', mode='eval')
        ops.extend([
            (bp.LOAD_CONST, eval),
            (bp.LOAD_CONST, op_code),
            (bp.LOAD_FAST, 'toolkit'),
            (bp.LOAD_FAST, 'f_globals'),
            (bp.CALL_FUNCTION, 0x0003),
            # When instantiating a Declaration, it is called without
            # identifiers, so that it creates it's own new identifier
            # scope. This means that derived declarations share ids,
            # but the composed children have an isolated id space.
            (bp.LOAD_CONST, None),
            (bp.LOAD_FAST, 'toolkit'),
            (bp.CALL_FUNCTION, 0x0002),
            (bp.STORE_FAST, name),
        ])
        
        if node.identifier:
            ops.extend([
                (bp.LOAD_FAST, name),
                (bp.LOAD_FAST, 'identifiers'),
                (bp.LOAD_CONST, node.identifier),
                (bp.STORE_SUBSCR, None),
            ])

        for item in node.body:
            self.visit(item)
        
        name_stack.pop()
        ops.extend([
            # foo._subcomponents.append(button)
            (bp.LOAD_FAST, name_stack[-1]),
            (bp.LOAD_ATTR, '_subcomponents'),
            (bp.LOAD_ATTR, 'append'),
            (bp.LOAD_FAST, name),
            (bp.CALL_FUNCTION, 0x0001),
            (bp.POP_TOP, None),
        ])


#------------------------------------------------------------------------------
# Defn Compiler
#------------------------------------------------------------------------------
class _DefnCollector(object):
    """ A private class that is used by the DefnCompiler to collect the
    components created when calling a defn. It also manages returning 
    the proper results depending on how many items were created.

    """
    __slots__ = ('_subcomponents',)

    def __init__(self):
        self._subcomponents = []

    def results(self):
        """ Computes the proper return results for a defn depending on
        how many components were created:
            
            n == 0 -> None
            n == 1 -> components
            n > 1  -> list of components
        
        """
        cmpnts = self._subcomponents
        n = len(cmpnts)
        if n == 0:
            res = None
        elif n == 1:
            res = cmpnts[0]
        else:
            res = cmpnts
        return res


class DefnCompiler(_NodeVisitor):
    """ A visitor which compiles a Defn node into a code object.

    """
    def __init__(self):
        self.ops = []
        self.name_gen = _var_name_generator()
        self.name_stack = []

    @classmethod
    def compile(cls, node):
        """ Compiles the given Defn node into a code object. The bytecode
        generated is similar to that for the Declaration node, with the
        exception that a Defn introduces arguments into the scope that
        need to be taken into account.

        """
        compiler = cls()
        compiler.visit(node)
        ops = compiler.ops
        code = byteplay.Code(ops, [], node.parameters.names, False, False,
                             True, node.name, 'Enaml', node.lineno, node.doc)
        return code.to_code()

    def visit_Defn(self, node):
        """ Creates the bytecode ops for a defn node.

        """
        bp = byteplay
        ops = self.ops
        name_stack = self.name_stack

        name = self.name_gen.next()
        name_stack.append(name)

        # defn FooBar(a, b, c):
        #     f_locals = locals()
        #     identifiers = {}
        #     identifiers.update(f_locals)
        #     f_globals = globals()
        #     toolkit = Toolkit.active_toolkit()
        #     merged_globals = {}
        #     merged_globals.update(toolkit)
        #     merged_globals.update(f_globals)
        #     root = _DefnCollector()
        ops.extend([
            # f_locals = locals()
            (bp.LOAD_GLOBAL, 'locals'),
            (bp.CALL_FUNCTION, 0x0000),
            (bp.STORE_FAST, 'f_locals'),

            # identifiers = {}
            # identifiers.update(f_locals)
            (bp.BUILD_MAP, 0),
            (bp.DUP_TOP, 0),
            (bp.LOAD_ATTR, 'update'),
            (bp.LOAD_FAST, 'f_locals'),
            (bp.CALL_FUNCTION, 0x0001),
            (bp.POP_TOP, None),
            (bp.STORE_FAST, 'identifiers'),

            # f_globals = globals()
            (bp.LOAD_GLOBAL, 'globals'),
            (bp.CALL_FUNCTION, 0x0000),
            (bp.STORE_FAST, 'f_globals'),

            # toolkit = Toolkit.active_toolkit()
            (bp.LOAD_CONST, Toolkit),
            (bp.LOAD_ATTR, 'active_toolkit'),
            (bp.CALL_FUNCTION, 0x0000),
            (bp.STORE_FAST, 'toolkit'),

            # eval_globals = {}
            # eval_globals.update(toolkit)
            # eval_globals.update(f_globals)
            (bp.BUILD_MAP, 0),
            (bp.DUP_TOP, None),
            (bp.LOAD_ATTR, 'update'),
            (bp.DUP_TOP, None),
            (bp.LOAD_FAST, 'toolkit'),
            (bp.CALL_FUNCTION, 0x0001),
            (bp.POP_TOP, None),
            (bp.LOAD_FAST, 'f_globals'),
            (bp.CALL_FUNCTION, 0x0001),
            (bp.POP_TOP, None),
            (bp.STORE_FAST, 'merged_globals'),

            # root = _DefnCollector()
            (bp.LOAD_CONST, _DefnCollector),
            (bp.CALL_FUNCTION, 0x0000),
            (bp.STORE_FAST, name),
        ])

        for item in node.body:
            self.visit(item)
        
        name_stack.pop()

        # return root.results()
        ops.extend([
            (bp.LOAD_FAST, name),
            (bp.LOAD_ATTR, 'results'),
            (bp.CALL_FUNCTION, 0x0000),
            (bp.RETURN_VALUE, None),
        ])

    def visit_AttributeBinding(self, node):
        """ Creates the bytecode ops for an attribute binding. This
        visitor handles loading and calling the appropriate operator.

        """
        # XXX handle BoundCodeBlock instead of just BoundExpression
        bp = byteplay
        ops = self.ops
        name_stack = self.name_stack

        # Grab the ast and code object for the expression. These will
        # be passed to the binding operator.
        expr_ast = node.binding.expr.py_ast
        expr_code = node.binding.expr.code
        op_code = compile(node.binding.op, 'Enaml', mode='eval')

        # A binding is accomplished by loading the appropriate binding
        # operator function and passing it the a number of arguments:
        #
        # op = eval('__operator_Equal__', merged_globals, f_locals)
        # op(item, 'a', <ast>, <code>, f_globals, toolkit, identifiers)
        ops.extend([
            (bp.LOAD_CONST, eval),
            (bp.LOAD_CONST, op_code),
            (bp.LOAD_FAST, 'merged_globals'),
            (bp.LOAD_FAST, 'f_locals'),
            (bp.CALL_FUNCTION, 0x0003),
            (bp.LOAD_FAST, name_stack[-1]),
            (bp.LOAD_CONST, node.name),
            (bp.LOAD_CONST, expr_ast),
            (bp.LOAD_CONST, expr_code),
            (bp.LOAD_FAST, 'f_globals'),
            (bp.LOAD_FAST, 'toolkit'),
            (bp.LOAD_FAST, 'identifiers'),
            (bp.CALL_FUNCTION, 0x0007),
            (bp.POP_TOP, None),
        ])

    def visit_Instantiation(self, node):
        """ Create the bytecode ops for a component instantiation. This 
        visitor handles calling another derived component and storing
        its identifier, if given.
        
        """
        bp = byteplay
        ops = self.ops
        name_stack = self.name_stack

        # This is similar logic to visit_Declaration
        name = self.name_gen.next()
        name_stack.append(name)

        op_code = compile(node.name, 'Enaml', mode='eval')
        ops.extend([
            # item = eval('Foo', merged_globals, f_locals)(None, toolkit)
            (bp.LOAD_CONST, eval),
            (bp.LOAD_CONST, op_code),
            (bp.LOAD_FAST, 'merged_globals'),
            (bp.LOAD_FAST, 'f_locals'),
            (bp.CALL_FUNCTION, 0x0003),
            (bp.LOAD_CONST, None),
            (bp.LOAD_FAST, 'toolkit'),
            (bp.CALL_FUNCTION, 0x0002),
            (bp.STORE_FAST, name),
        ])
        
        if node.identifier:
            ops.extend([
                (bp.LOAD_FAST, name),
                (bp.LOAD_FAST, 'identifiers'),
                (bp.LOAD_CONST, node.identifier),
                (bp.STORE_SUBSCR, None),
            ])

        for item in node.body:
            self.visit(item)
        
        name_stack.pop()
        ops.extend([
            # foo._subcomponents.append(button)
            (bp.LOAD_FAST, name_stack[-1]),
            (bp.LOAD_ATTR, '_subcomponents'),
            (bp.LOAD_ATTR, 'append'),
            (bp.LOAD_FAST, name),
            (bp.CALL_FUNCTION, 0x0001),
            (bp.POP_TOP, None),
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
    def compile(cls, module_ast, module_dict):
        """ The main entry point of the compiler.

        Parameters
        ----------
        module_ast : Instance(enaml_ast.Module)
            The enaml module ast node that should be compiled.
        
        module_dict : dict
            The dictionary of the Python module into which we are
            compiling the enaml code.
        
        """
        compiler = cls(module_dict)
        compiler.visit(module_ast)

    def __init__(self, module_dict):
        """ Initialize a compiler instance.

        Parameters
        ----------
        module_dict : dict
            The module dictionary into which the compiled objects are 
            placed.
        
        """
        # This ensures that the key '__builtins__' exists in the mod dict.
        exec '' in module_dict
        self.global_ns = module_dict

    def visit_Module(self, node):
        """ The module node visitory method. Used internally by the
        compiler.

        """
        if node.doc:
            self.global_ns['__doc__'] = node.doc
        for item in node.body:
            self.visit(item)
    
    def visit_Python(self, node):
        """ A visitor which adds a chunk of raw Python into the module.

        """
        try:
            exec node.code in self.global_ns
        except Exception as e:
            msg = ('Unable to evaluate raw Python code on lineno %s. '
                   'Original exception was %s.')
            exc_type = type(e)
            raise exc_type(msg % (node.lineno, e))
        
    def visit_Import(self, node):
        """ The import statement visitor method. This ensures that imports
        are performed with the enaml import hook in-place.

        """
        with imports():
            try:
                exec node.code in self.global_ns
            except Exception as e:
                msg = ('Unable to evaluate import on lineno %s. '
                       'Original exception was %s.')
                exc_type = type(e)
                raise exc_type(msg % (node.lineno, e))

    def visit_Declaration(self, node):
        """ The declaration node visitor. This will add an instance
        of EnamlDeclaration to the module.

        """
        func_code = DeclarationCompiler.compile(node)
        func = types.FunctionType(func_code, self.global_ns)
        wrapper = _decl_wrapper_gen(func)
        self.global_ns[node.name] = wrapper
    
    def visit_Defn(self, node):
        """ The defn node visitor. This will add an instance of EnamlDefn
        to the module.

        """
        # XXX Handle arg defaults
        func_code = DefnCompiler.compile(node)
        func = types.FunctionType(func_code, self.global_ns)
        self.global_ns[node.name] = func

