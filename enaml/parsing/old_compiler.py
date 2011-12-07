#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from . import enaml_ast
from .. import imports
from .virtual_machine import (LOAD_GLOBAL, LOAD_LOCAL, LOAD_CONST,
                              LOAD_GLOBALS_CLOSURE, LOAD_LOCALS_CLOSURE, 
                              GET_ITEM, STORE_LOCAL, EVAL, CALL, DUP_TOP,
                              POP_TOP, UNPACK_SEQUENCE, ENAML_ADD_CHILDREN, 
                              GET_ITER, FOR_ITER, JUMP_ABSOLUTE, ROT_TWO,
                              ENAML_CALL, evalcode)

from ..exceptions import EnamlSyntaxError
from ..view import View


#------------------------------------------------------------------------------
# Enaml Definition Object
#------------------------------------------------------------------------------
class EnamlDefinition(object):  
    """ The Python class which represents a defn block in Enaml source
    code. Instances of this class are callable and are added to the
    module dictionary (1 per defn block). When called, these objects
    populate an initial local namespace and then hand off to the 
    Enaml virtual machine for executing the function body.

    """
    def __init__(self, name, doc, code, args, defaults, global_ns):
        """ Initialize an EnamlDefinition.

        Parameters
        ----------
        name : string
            The name of the defn block.
        
        doc : string
            The docstring for the defn block.

        code : list
            The list of instruction to execute in the vm when called.
        
        args : list of strings
            The list of all the parameter names in the defn block 
            declaration, ordered from left to right.
        
        defaults : list of objects
            The list of default keyword values. The values are matched
            with the argument names from right to left starting at the
            right side of both lists.
        
        global_ns : dict
            The module dict in which this definition lives.
        
        """
        self.__name__ = name
        self.__doc__ = doc
        self.__code__ = code
        self.__args__ = args
        self.__defaults__ = defaults
        self.__globals__ = global_ns

    def __call__(self, *args, **kwargs):
        """ Returns a view object created by the call to the defn 
        function.

        """
        components, ns = self.__enaml_call__(*args, **kwargs)
        view = View(components=components, ns=ns)
        return view

    def __enaml_call__(self, *args, **kwargs):
        """ Execute the instruction code in the Enaml virtual machine.

        Paramters
        ---------
        *args, **kwargs
            The arguments and keywords which comprise the initial local
            scope of the defn call.
        
        Returns
        -------
        results : (widgets, ns)
            The sequence of widgets and the local namespace created
            by the call.
        
        """
        f_locals = self._build_locals(args, kwargs)
        f_globals = self.__globals__
        return evalcode(self.__code__, f_globals, f_locals)

    def _build_locals(self, args, kwargs):
        """ Creates an initial local scope dictionary given the arg and
        kwargs with which the definition was called. Performs appropriate
        argument checking for consistency with Python call semantics.
        This method is used internally by the definition.

        """
        __name__ = self.__name__
        __args__ = self.__args__
        __defaults__ = self.__defaults__

        n_params = len(__args__)
        n_defaults = len(__defaults__)
        n_required = n_params - n_defaults
        n_args = len(args)
        n_kwargs = len(kwargs)
        n_supplied = n_args + n_kwargs

        if n_params > 0 and n_defaults == 0 and n_supplied != n_params:
            msg = '%s() takes exactly %s arguments (%s given)'
            raise TypeError(msg % (__name__, n_params, n_supplied))
        elif n_supplied < n_required:
            msg = '%s() requires at least %s arguments (%s given)'
            raise TypeError(msg % (__name__, n_required, n_supplied))
        elif n_supplied > n_params:
            msg = '%s() takes at most %s arguments (%s given)'
            raise TypeError(msg % (__name__, n_params, n_supplied))
               
        scope = {}
        
        for name, value in zip(__args__[:n_args], args):
            scope[name] = value
        
        for name, value in kwargs.iteritems():
            if name not in __args__:
                msg = '%s() got an unexpected keyword argument `%s`'
                raise TypeError(msg % (self.name, name)) 
            if name in scope:
                msg = '%s() got multiple values for keyword `%s`'
                raise TypeError(msg % (self.name, name))
            scope[name] = value
        
        for key, value in zip(__args__[-n_defaults:], __defaults__):
            if key not in scope:
                scope[key] = value

        return scope


#------------------------------------------------------------------------------
# Compiler
#------------------------------------------------------------------------------
class _Mangler(object):
    """ A name mangler used by the enaml defn body compiler to create
    mangled names for use in anonymous assigments. For each new instance
    of this class, once can call the instance with a string and get back
    a mangled name of the form '_<string>_<n>' where n is the nth time
    the instance has been called with this string.

    Example
    -------
    >>> mangle = _Mangler()
    >>> mangle('Panel')
    _Panel_0
    >>> mangle('Panel')
    _Panel_1
    >>> mangle('Foo')
    _Foo_0
    >>> mangle = _Mangler()
    >>> mangle('Panel')
    _Panel_0

    """
    @staticmethod
    def _mangle(name):
        i = 0
        while True:
            yield '_%s_%s' % (name, i)
            i += 1

    def __init__(self):
        self._manglers = {}

    def __call__(self, name):
        manglers = self._manglers
        if name in manglers:
            mangler = manglers[name]
        else:
            mangler = manglers[name] = self._mangle(name)
        return mangler.next()


class DefnBodyCompiler(object):
    """ A compiler for the body of a defn statement.

    This compiler performs the majority of the compilation work 
    for enaml. It converts the body of a defn block into a set
    of virtual machine instructions. Coupled with the appropriate
    namespaces, these instructions can be executed by the virtual
    machine to build the ui tree.

    The main entry point is the `compile` classmethod.

    """
    @classmethod
    def compile(cls, local_names, body):
        """ The main entry point of the compiler.

        Parameters
        ----------
        local_names : set
            The initial set of local_names that are available to the 
            body as the result of the function call (the argument names)
            This set is updated in-place during compilation with new
            local variables as they are defined.
        
        body : list
            The list ast nodes that comprise the body of the defn
            block.
        
        Returns
        -------
        result : list
            The list of virtual machine instructions for this defn block.
        
        """
        compiler = cls(local_names)
        for item in body:
            compiler.visit(item)
        return compiler.instructions

    def __init__(self, local_names):
        """ Initialize a compiler instance.

        Parameters
        ----------
        local_names : set
            The initial set of local names. Will be updated in-place.

        """
        self.mangle = _Mangler()
        self.local_names = local_names
        self.instructions = []

    def visit(self, node):
        """  The main visitor dispatch method. Used internally by the
        compiler.

        """
        name = 'visit_%s' % node.__class__.__name__
        method = getattr(self, name, self.default_visit)
        method(node)

    def default_visit(self, node):
        """ The default visitor method. Used internally by the compiler.

        """
        raise ValueError('Unhandled Node %s.' % node)

    def visit_EnamlCall(self, node):
        """ The vistor method for the call node. Used internally by the
        compiler.

        """
        local_names = self.local_names
        instructions = self.instructions

        # In enaml, all calls that create widgets return two items: 
        # a sequence of components (even if only 1), and a namespace dict.
        # The current top of the stack is the sequence that was returned
        # by the last call. In order to use it as a parent, and also let
        # it be returned to its caller, we need to duplicate it.
        inst = (DUP_TOP, None)
        instructions.append(inst)
        
        # Lookup the symbol which we'll be calling
        name = node.name
        if name in local_names:
            inst = (LOAD_LOCAL, name)
        else:
            inst = (LOAD_GLOBAL, name)
        instructions.append(inst)

        # Load the args and kwargs for the call. Note that the args
        # and kwargs get placed on the stack from left to right. The
        # virtual machine will reverse them as it pops them off so 
        # that they get passed in the correct order.
        n_args = 0
        n_kwargs = 0
        for arg in node.arguments:
            if isinstance(arg, enaml_ast.EnamlArgument):
                n_args += 1
            else:
                n_kwargs += 1
            self.visit(arg)
        
        # Execute the call operation. The sequence and the dict that is 
        # returned by the call are each pushed onto the stack separately.
        inst = (ENAML_CALL, (n_args, n_kwargs))
        instructions.append(inst)

        # At this point, the top two items in the stack are
        # | ... | sequence | namespace dict
        # We need to handle any namespace captures from this namespace.
        for capture in node.captures:
            ns_name = capture.ns_name
            store_name = capture.name

            # Duplicate the TOS so we can consume a reference to the
            # namespace object.
            inst = (DUP_TOP, None)
            instructions.append(inst)

            # If the name to lookup in the namespace is not '*',
            # This indicates we should capture that item out of the ns.
            if ns_name != '*':
                inst = (GET_ITEM, ns_name)
                instructions.append(inst)
                
            # Finally we store away the item. If the ns_name was '*'
            # then we are storing away the entire namespace
            inst = (STORE_LOCAL, store_name)
            instructions.append(inst)

        # After we're done with the captures, we can discard the namespace.
        inst = (POP_TOP, None)
        instructions.append(inst)

        # In order to unpack the return sequence values into local 
        # variables, and still have values to add as children to the
        # parent, we need to duplicate the top.
        inst = (DUP_TOP, None)
        instructions.append(inst)

        # Unpack the TOS sequence into local variables. If no unpack 
        # name is provided (an anonymous call) we generate a mangled 
        # name into which we do the assigment. This provides two things:
        # 1) consistency of handling return values
        # 2) the ability to refer to `anonymous` results if one knows
        #    the mangling semantics.
        #
        # The vm special cases unpacking sequences into 1 name. If
        # the sequence is of length-1, then the single value is 
        # unpacked. Otherwise, the entire sequence is pushed back
        # onto the stack. This means that doing Field -> my_field will
        # cause `my_field` to be bound to the Field object instead of
        # a length-1 tuple (which is what the Field call actually returns)
        unpack = node.unpack
        if not unpack:
            unpack = [self.mangle(name)]
        
        n_unpack = len(unpack)
        inst = (UNPACK_SEQUENCE, n_unpack)
        instructions.append(inst)
        for unpack_name in unpack:
            inst = (STORE_LOCAL, unpack_name)
            instructions.append(inst)
            local_names.add(unpack_name)

        # Visit the body of the call node. This is a list comprised of
        # (at most) two types of nodes: assignment nodes, call nodes.
        for item in node.body:
            self.visit(item)
        
        # Finally 'return' from the call by adding the children to their
        # parent. At this point, the top of the stack is the sequence of 
        # children we want to add, and the next item is the parent to which
        # we want to add them. This parent must be a sequence of length-1.
        # If it's not, the vm will raise a runtime error, since it makes no 
        # sense to add to multiple things.
        inst = (ENAML_ADD_CHILDREN, None)
        instructions.append(inst)

    def visit_EnamlArgument(self, node):
        """ The visitor method for handling arguments passed to 
        callable objects. Used internally by the compiler.

        """
        # Creating an argument follows the process:
        # 1) Load the code object for the argument expression
        # 4) Eval the code in the collapsing scope and push the results
        instructions = self.instructions
        code = compile(node.py_ast, 'Enaml', mode='eval')
        inst = (LOAD_CONST, code)
        instructions.append(inst)
        inst = (EVAL, None)
        instructions.append(inst)

    def visit_EnamlKeywordArgument(self, node):
        """ The visitor method for handling keyword arguments passed
        to callable objects. Used internally by the compiler.

        """
        # Creating an argument follows the process:
        # 1) Load the name for the keyword argument
        # 2) Load the code object for the keyword expression
        # 5) Eval the code in the collapsing scope and push the results
        instructions = self.instructions
        code = compile(node.py_ast, 'Enaml', mode='eval')
        inst = (LOAD_CONST, node.name)
        instructions.append(inst)
        inst = (LOAD_CONST, code)
        instructions.append(inst)
        inst = (EVAL, None)
        instructions.append(inst)

    def visit_EnamlAssignment(self, node):
        """ The visitor method for the assignment node. Used internally
        by the compiler.

        """
        instructions = self.instructions

        lhs = node.lhs
        op = node.op
        py_ast = node.rhs.py_ast

        # There are two cases for an assignment that need to be handled:
        # 1) The assignment is being done to a name, which implicitly
        #    means that the assignment should be performed to that attr
        #    on every element in the sequence on TOS.
        # 2) The assignment is being done to a getattr-style expression
        #    which means that the assignment is being explicity performed
        #    on a single one of the return sequence objects.

        # Case 1) Mapping onto each item in the sequence
        if isinstance(lhs, enaml_ast.EnamlName):
            # Create an iterator from the tos over which we will loop
            # and perform the assignment operations
            inst = (DUP_TOP, None)
            instructions.append(inst)
            inst = (GET_ITER, None)
            instructions.append(inst)
            
            # Create the list of binding instructions that form the inner 
            # body of the loop.
            bind_insts = self.create_binding_insts(op, lhs.name, py_ast)

            # The loop_idx is the absolute instruction index to which the
            # vm will jump at the end of each succesful run of the loop.
            # 
            # The jump_target is the absolute instruction index to which
            # the vm will jump once the iterator is exhausted. The +2 
            # offset is used to account for the FOR_ITER and JUMP_ABSOLUTE 
            # instructions that bound the loop body instructions.
            loop_idx = len(instructions)
            jump_target = loop_idx + len(bind_insts) + 2
            inst = (FOR_ITER, jump_target)
            instructions.append(inst)
            instructions.extend(bind_insts)
            inst = (JUMP_ABSOLUTE, loop_idx)
            instructions.append(inst)

        # Case 2) Assigning to an explicit return item
        elif isinstance(lhs, enaml_ast.EnamlGetattr):
            # There are two types of lhs getattr expressions allowed
            # by the enaml parser:
            # 1) plain `foo.bar` style getattr
            # 2) `some_sequence[some_int].some_attr` style getattr
            #
            # This covers the practical use cases of assignment in enaml.
            root = lhs.root
            attr_name = lhs.attr
            root_name = root.name

            # Case 1) `foo.bar` style getattr
            if isinstance(root, enaml_ast.EnamlName):
                inst = (LOAD_LOCAL, root_name)
                instructions.append(inst)
                insts = self.create_binding_insts(op, attr_name, py_ast)
                instructions.extend(insts)
                    
            # Case 2) `some_sequence[some_int].some_attr` style getattr
            elif isinstance(root, enaml_ast.EnamlIndex):
                inst = (LOAD_LOCAL, root_name)
                instructions.append(inst)
                inst = (GET_ITEM, root.idx)
                instructions.append(inst)
                insts = self.create_binding_insts(op, attr_name, py_ast)
                instructions.extend(insts)

            else:
                msg = 'The parser should not allow this to happen'
                raise EnamlSyntaxError(msg)

        else:
            msg = 'The parser should not allow this to happen'
            raise EnamlSyntaxError(msg)

    def create_binding_insts(self, op, attr_name, py_ast):
        """ Creates a new list of vm instructions for binding a python
        expression to the attribute of an enaml widget. Used internally
        by the compiler.

        """
        # The top of the stack will be the enaml widget object which 
        # has the attribute to which we want to bind. It is assumed
        # the tos is appropriately duplicated and we are free to consume
        # the top of the stack.
        #
        # The semantics here are:
        # 1) Load the operator that will handle the expression binding.
        # 2) Rotate the top 2 items so that the operator is under the object.
        # 3) Load the remaining args for the operator call 
        #    (attribute_name, ast, code_obj, globals, locals)
        # 4) Call the operator.
        # 5) Pop the top of the stack since the operator returns None.
        #
        # The operators are looked up as specially named objects which 
        # are provided by the toolkit and can therefore be looked up 
        # by default in the global namespace. It also means that they
        # can be overridden through dependency inject via function
        # arguments or as members of the module's dict.
        local_names = self.local_names
        instructions = []

        # The ast is compiled into a code object now, instead of allowing
        # the operators to do it because then it would be compiled every
        # time the defn is called, instead of just once as it needs to be
        # since an expression code object is reusable across mutliple
        # independent namespaces.
        code = compile(py_ast, 'Enaml', mode='eval')

        # Load the operator
        if op in local_names:
            inst = (LOAD_LOCAL, op)
        else:
            inst = (LOAD_GLOBAL, op)
        instructions.append(inst)
        
        # ROT_TWO to put the operator under its first argument.
        inst = (ROT_TWO, None)
        instructions.append(inst)
        
        # Load the rest of the arguments for the operator call
        inst = (LOAD_CONST, attr_name)
        instructions.append(inst)
        inst = (LOAD_CONST, py_ast)
        instructions.append(inst)
        inst = (LOAD_CONST, code)
        instructions.append(inst)
        inst = (LOAD_GLOBALS_CLOSURE, None)
        instructions.append(inst)
        inst = (LOAD_LOCALS_CLOSURE, None)
        instructions.append(inst)

        # Call the operator with 
        # (obj, name, py_ast, code, globals_closure, locals_closure)
        inst = (CALL, (6, 0))
        instructions.append(inst)

        # Pop and discard the None result from the operator
        inst = (POP_TOP, None)
        instructions.append(inst)

        return instructions
        

class EnamlCompiler(object):
    """ A compiler that will compile an enaml module ast node.
    
    The entry point is the `compile` classmethod which will compile
    the ast into appropriate python object and place the results 
    in the provided module dictionary.

    """
    @classmethod
    def compile(cls, enaml_module_ast, module_dict):
        """ The main entry point of the compiler.

        Parameters
        ----------
        enaml_module_ast : Instance(enaml_ast.EnamlModule)
            The enaml module ast node that should be compiled.
        
        module_dict : dict
            The dictionary of the Python module into which we are
            compiling the enaml code.

        Returns
        -------
        result : None
            The compiled results are added to the provided module
            dictionary.
        
        """
        compiler = cls(module_dict)
        compiler.visit(enaml_module_ast)

    def __init__(self, module_dict):
        """ Initialize a compiler instance.

        Parameters
        ----------
        module_dict : dict
            The module dictionary into which the compiled objects
            are placed.
        
        """
        # This ensures that __builtins__ exists in the module dict.
        exec('', {}, module_dict)
        self.global_ns = module_dict

    def visit(self, node):
        """ The main vistor dispatch method. Used internally by the
        compiler.

        """
        name = 'visit_%s' % node.__class__.__name__
        method = getattr(self, name, self.default_visit)
        method(node)

    def default_visit(self, node):
        """ The default visitor method. Used internally by the 
        compiler.

        """
        raise ValueError('Unhandled Node %s.' % node)

    def visit_EnamlModule(self, node):
        """ The module node visitory method. Used internally by the
        compiler.

        """
        if node.doc:
            self.global_ns['__doc__'] = node.doc
        for item in node.body:
            self.visit(item)
    
    def visit_EnamlRawPython(self, node):
        py_txt = node.py_txt
        code = compile(py_txt, '<Enaml>', mode='exec')
        exec code in self.global_ns

    def visit_EnamlImport(self, node):
        """ The import statement visitory method. Used internally 
        by the compiler.

        """
        # The import statements are currently normal python
        # ast trees. In the future, this will probably be
        # extended to support an enaml import.
        # 
        # The global ns must be passed as the locals since
        # it's a mapping type and not a real dictionary.
        # The effect is the same.
        code = compile(node.py_ast, 'Enaml', mode='exec')
        # Enable the Enaml import hook to allow inter-enaml imports if they have
        # not been already.
        with imports():
            exec(code, self.global_ns)

    def visit_EnamlDefine(self, node):
        """ The definition node visitory. Used internally by the 
        compiler.

        """
        # The default keyword parameters for a definition are computed
        # once per compilation (just like in Python) and at the time
        # the definition appears in the module. The only scope of the
        # default parameter expressions is the global ns (just like 
        # Python).
        #
        # The global ns must be passed as the locals since
        # it's a mapping type and not a real dictionary.
        # The effect is the same.
        computed_defaults = []
        for expr in node.parameters.defaults:
            code = compile(expr, 'Enaml', mode='eval')
            computed = eval(code, self.global_ns)
            computed_defaults.append(computed)
        
        # The definition body compiler requires an initial set of 
        # names that will appear in the local scope. This is an 
        # optimization so we don't have to lookup locals -> globals
        # on everything and can go straight to locals or globals
        # based on what names exist in the local namespace (which
        # is trackable)
        args = node.parameters.args 
        instructions = DefnBodyCompiler.compile(set(args), node.body)

        # The definition compiler just gives us an instruction set.
        # The instructions are executed by a 'function-like' object
        # which, when called, creates the local namespace and dispatches
        # to the virtual machine to execute the instruction set.
        name = node.name
        doc = node.doc
        definition = EnamlDefinition(
            name, doc, instructions, args, computed_defaults, self.global_ns,
        )

        # The defintion is a normal callable python object that we
        # add to the global_ns and is thus an importable object
        self.global_ns[name] = definition


