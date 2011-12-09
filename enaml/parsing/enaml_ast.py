#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
class ASTNode(object):
    """ The base Enaml AST node.

    Attributes
    ----------
    lineno : int
        The line number in the source code that created this node.
    
    """
    __slots__ = ('lineno',)

    def __init__(self, lineno):
        self.lineno = lineno

    def __repr__(self):
        return self.__class__.__name__

    def __str__(self):
        return repr(self)
            

class Module(ASTNode):
    """ An AST node representing an Enaml module.

    Attributes
    ----------
    doc : str
        The module's documentation string.
    
    body : list
        A list of ast nodes comprising the body of the module.
    
    """
    __slots__ = ('doc', 'body',)

    def __init__(self, doc, body, lineno):
        super(Module, self).__init__(lineno)
        self.doc = doc
        self.body = body


class Python(ASTNode):
    """ An AST node representing a chunk of pure Python code.

    Attributes
    ----------
    py_ast : ast.AST
        A Python ast node.
    
    code : types.CodeType
        The compiled Python code object for the py_ast.
    
    """
    __slots__ = ('py_ast', 'code')

    def __init__(self, py_ast, code, lineno):
        super(Python, self).__init__(lineno)
        self.py_ast = py_ast
        self.code = code


class Import(Python):
    """ A _PyNode representing a normal Python import statement.

    """
    __slots__ = ()


class Declaration(ASTNode):
    """ An AST node representing an Enaml declaration.

    Attributes
    ----------
    name : str
        The name of the declaration.
    
    base : Python
        A Python node which represents the base type of the declaration.
    
    identifier : str
        The local identifier to use for instances of the declaration.
    
    doc : str
        The documentation string for the declaration.
    
    body : list
        A list of AST nodes that comprise the body of the declaration.
    
    """
    __slots__ = ('name', 'base', 'identifier', 'doc', 'body')

    def __init__(self, name, base, identifier, doc, body, lineno):
        super(Declaration, self).__init__(lineno)
        self.name = name
        self.base = base
        self.identifier = identifier
        self.doc = doc
        self.body = body


class Instantiation(ASTNode):
    """ An AST node representing a declaration instantiation.

    Attributes
    ----------
    name : str
        The name of declaration being instantiated.
    
    identifier : str
        The local identifier to use for the new instance.
    
    body : list
        A list of AST nodes which comprise the instantiation body.
    
    """
    __slots__ = ('name', 'identifier', 'body')

    def __init__(self, name, identifier, body, lineno):
        super(Instantiation, self).__init__(lineno)
        self.name = name
        self.identifier = identifier
        self.body = body


class AttributeBinding(ASTNode):
    """ An AST node which represents an expression attribute binding.

    Attributes
    ----------
    name : str
        The name of the attribute being bound.
    
    binding : ast node
        The ast node which represents the binding.
    
    """
    __slots__ = ('name', 'binding')

    def __init__(self, name, binding, lineno):
        super(AttributeBinding, self).__init__(lineno)
        self.name = name
        self.binding = binding


class BoundExpression(ASTNode):
    """ An ast node which represents a bound expression.

    Attributes
    ----------
    op : str
        The name of the operator that will perform the binding.
    
    expr : Python
        A Python ast node that reprents the bound expression.
    
    """
    __slots__ = ('op', 'expr')

    def __init__(self, op, expr, lineno):
        super(BoundExpression, self).__init__(lineno)
        self.op = op
        self.expr = expr


class BoundCodeBlock(Python):
    """ An ast Node which represents a bound block of Python code.

    """
    __slots__ = ()


class Defn(ASTNode):
    """ An ast Node which represents a defn block.

    Attributes
    ----------
    name : str
        The name of the defn block.
    
    parameters : Parameters
        A Parameters node for the parameters passed to the defn.
    
    doc : str
        The documentation string of the defn.
    
    body : list
        A list of ast nodes comprising the body of the defn.
    
    """
    __slots__ = ('name', 'parameters', 'doc', 'body')

    def __init__(self, name, parameters, doc, body, lineno):
        super(Defn, self).__init__(lineno)
        self.name = name
        self.parameters = parameters
        self.doc = doc
        self.body = body


class Parameters(ASTNode):
    """ An ast Node representing the parameters definition of a defn.

    Attributes
    ----------
    names : list
        A list of strings which are the names of the parameters.
    
    defaults : list
        A list of Python nodes representing any default parameter
        values.

    """
    __slots__ = ('names', 'defaults')
    
    def __init__(self, names, defaults, lineno):
        super(Parameters, self).__init__(lineno)
        self.names = names
        self.defaults = defaults
        

class Call(ASTNode):
    """ An ast Node representing a defn call.

    Attributes
    ----------
    name : str
        The name of the defn being called.
    
    arguments : list
        A list of Argument or KeywordArgument nodes which are the 
        arguments being passed to the defn.
    
    """
    __slots__ = ('name', 'arguments')

    def __init__(self, name, arguments, lineno):
        super(Call, self).__init__(lineno)
        self.name = name
        self.arguments = arguments


class Argument(Python):
    """ An ast node representing an argument passed to a defn.
    
    """    
    __slots__ = ()


class KeywordArgument(ASTNode):
    """ An ast node representing a keyword argument passed to a defn.

    Attributes
    ----------
    name : str
        The name of the keyword argument.
    
    argument : Argument
        An Argument node which is the value of the keyword argument.
    
    """
    __slots__ = ('name', 'argument')

    def __init__(self, name, argument, lineno):
        super(KeywordArgument, self).__init__(lineno)
        self.name = name
        self.argument = argument

