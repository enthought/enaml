#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from abc import ABCMeta, abstractmethod

from .byteplay import (
    LOAD_NAME, CALL_FUNCTION, ROT_THREE, LOAD_CONST, LOAD_ATTR, ROT_TWO,
    BUILD_TUPLE, RETURN_VALUE,
)


#------------------------------------------------------------------------------
# Abstract Inverter
#------------------------------------------------------------------------------
class AbstractInverter(object):
    """ An abstract base class which defined the api for creating code
    inverter objects. An inverter is responsible for converting a code
    list supplied by an expression into the inverse of that expression
    which applies the new value onto the expression. For example:

    The expression:
                    getattr(foo, 'bar')
    
    Becomes:
                    setattr(foo, 'bar', value)
    
    Likewise, the expression:
                    [spam.ham[0] for spam in foo][0].bar

    Would be translated into:
                    [spam.ham[0] for spam in foo][0].bar = value

    The value, among other information, is provided by the expression 
    by inserting the following names into the scope, which can be 
    retrieved with the LOAD_NAME op-code:
        
        _[expr] : The expression object
        _[obj]  : The component object which triggered the change
        _[name] : The attribute on the component which changed
        _[old]  : The old value of the attribute.
        _[new]  : The new value of the attribute which should be
                  applied to the inverted expression.
    
    The generated expression should return True if it successfully 
    completed the operation, False otherwise.

    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_inverted_code(self, code_list):
        """ Generates the byteplay code operations which represent
        the inverted expression. If the inverter is unable to invert
        the given expression, it should return None.

        Parameters
        ----------
        code_list : list of (op_code, op_arg)
            The list of byteplay code operations for the expression.

        Returns
        -------
        result : list of (op_code, op_arg) or None
            A new list of code ops for the inverted expression, or 
            None if the inverter is unable to invert the expression.
            The generated code, when executed, should return True if
            the operation was successful, False otherwise. Exceptions
            raised by the user code should be propagated.

        """
        raise NotImplementedError


#------------------------------------------------------------------------------
# Abstract Attribute Inverter 
#------------------------------------------------------------------------------
class AbstractAttributeInverter(AbstractInverter):
    """ An AbstractInverter subclass which converts a bytecode expression
    ending in LOAD_ATTR into an appropriate expression which calls a 
    delegate to do the setattr operation.

    """
    def get_inverted_code(self, code_list):
        """ Generates and returns a new code list for expressions ending
        in a LOAD_ATTR op_code.

        """
        attr_code, attr_arg = code_list[-2]
        if attr_code == LOAD_ATTR:
            handler = self.get_setattr_handler()
            new_code = code_list[:-2]
            new_code.extend([
                (LOAD_CONST, handler),
                (ROT_TWO, None),
                (LOAD_CONST, attr_arg),
                (LOAD_NAME, '_[new]'),
                (CALL_FUNCTION, 0x0003),
                (RETURN_VALUE, None),
            ])
            return new_code

    @abstractmethod
    def get_setattr_handler(self):
        """ Returns a function which accepts three arguments: an object,
        an attribute name, and a value, and performs a setattr operation
        with the items. The function that performs the operation should 
        return True on success and False on failure. This method must be 
        implemented by subclasses.

        """
        raise NotImplementedError


#------------------------------------------------------------------------------
# Generic Attribute Inverter
#------------------------------------------------------------------------------
class GenericAttributeInverter(AbstractAttributeInverter):
    """ A concrete implementation of AbstractAttributeInverter which 
    performs the attribute operation using the builtin setattr.

    """
    @staticmethod
    def _attribute_inverter(obj, name, value):
        """ Performs a setattr on the object and returns True.

        """
        setattr(obj, name, value)
        return True

    def get_setattr_handler(self):
        """ Returns the builtin setattr function which is used to 
        perform the set attribute operation.

        """
        return self._attribute_inverter


#------------------------------------------------------------------------------
# Abstract Call Inverter
#------------------------------------------------------------------------------
class AbstractCallInverter(AbstractInverter):
    """ An AbstractInverter subclass which converts a bytecode expression
    ending in a CALL_FUNCTION into an appropriate expression which calls a 
    delegate to do the setattr operation.

    """
    @staticmethod
    def _call_wrapper(handler):
        """ A call inverter helper function which takes the handler
        and returns a closure which will unpack the stack arguments, 
        calls the handler, the return its value.

        """
        def closure(func_obj, arg_tuple, arg_spec, value):
            nargs = arg_spec & 0xFF
            args = arg_tuple[:nargs]
            kwargs = dict(zip(arg_tuple[nargs::2], arg_tuple[nargs+1::2]))
            return handler(func_obj, args, kwargs, value)
        return closure

    def get_inverted_code(self, code_list):
        """ Generates and returns a new code list for expressions ending
        in a CALL_FUNCTION op_code.

        """
        func_code, func_arg = code_list[-2]
        if func_code == CALL_FUNCTION:
            handler = self._call_wrapper(self.get_call_handler())
            new_code = code_list[:-2]
            n_stack_args = (func_arg & 0xFF) + 2 * ((func_arg >> 8) & 0xFF)
            new_code.extend([
                (BUILD_TUPLE, n_stack_args),
                (LOAD_CONST, handler),
                (ROT_THREE, None),
                (LOAD_CONST, func_arg),
                (LOAD_NAME, '_[new]'),
                (CALL_FUNCTION, 0x0004),
                (RETURN_VALUE, None),
            ])
            return new_code

    @abstractmethod
    def get_call_handler(self):
        """ Returns a function which accepts four arguments: the object
        that would have been called, the arguments being passed, the
        keyword arguments being passed, and the value that should be
        applied. The function that performs the operation should return
        True on success and False on failure. This method must be 
        implemented by subclasses.

        """
        raise NotImplementedError


#------------------------------------------------------------------------------
# Getattr Inverter
#------------------------------------------------------------------------------
class GetattrInverter(AbstractCallInverter):
    """ A concrete implementation of AbstractCallInverter which inverts
    a call to getattr into a call to setattr.

    """
    @staticmethod
    def _getattr_inverter(func_obj, args, kwargs, value):
        """ Performs the getattr inversion provided that the function
        being called is the builtin getattr with an appropriate arg
        spec.

        """
        if func_obj is getattr:
            if len(args) >= 2 and len(kwargs) == 0:
                setattr(args[0], args[1], value)
                return True
        return False

    def get_call_handler(self):
        """ Returns a function which accepts four arguments: the object
        that would have been called, the arguments being passed, the
        keyword arguments being passed, and the value that should be
        applied.

        """
        return self._getattr_inverter


#------------------------------------------------------------------------------
# Abstract Name Inverter
#------------------------------------------------------------------------------
class AbstractNameInverter(AbstractInverter):
    """ An AbstractInverter subclass which converts a bytecode expression
    which consists soley of a LOAD_NAME op_code into an appropriate 
    expression which calls a delegate to do the setattr operation.

    """
    def get_inverted_code(self, code_list):
        """ Generates and returns a new code list for expressions which
        consist solely of a LOAD_NAME op_code.

        """
        name_code, name_arg = code_list[-2]
        if name_code == LOAD_NAME and len(code_list) == 3:
            handler = self.get_name_handler()
            new_code = code_list[:-2]
            new_code.extend([
                (LOAD_CONST, handler),
                (LOAD_NAME, '_[expr]'),
                (LOAD_NAME, '_[obj]'),
                (LOAD_NAME, '_[name]'),
                (LOAD_CONST, name_arg),
                (LOAD_NAME, '_[new]'),
                (CALL_FUNCTION, 0x0005),
                (RETURN_VALUE, None),
            ])
            return new_code

    @abstractmethod
    def get_name_handler(self):
        """ Returns a function which accepts five arguments: the 
        expression object which owns this inverter, the object which 
        owns the attribute that changed, the name of the attribute that
        changed, the name on which to store the value, and the value 
        which should be stored. The function that performs the operation
        should return True on success and False on failure. This method 
        must be implemented by subclasses.

        """
        raise NotImplementedError


#------------------------------------------------------------------------------
# Generic Name Inverter
#------------------------------------------------------------------------------
class ImplicitAttrInverter(AbstractNameInverter):
    """ A concrete implementation of AbstractNameInverter which inverts
    a name access into a setattr operation on an implicit attribute
    in the component hierarchy.

    """
    @staticmethod
    def _name_inverter(expr, obj, attr, store_name, value):
        """ Performs the name inversion by walking the component tree
        looking for an object which has an attribute of the right
        name. Will return False if no valid target is found, if the 
        name references an identifier, or if the assignment would 
        result in a direct cycle.

        """
        if store_name in expr.identifiers or attr == store_name:
            return False
        while obj is not None:
            if hasattr(obj, store_name):
                setattr(obj, store_name, value)
                return True
            else:
                obj = obj.parent
        return False

    def get_name_handler(self):
        """ Returns a function which accepts five arguments: the 
        expression object which owns this inverter, the object which 
        owns the attribute that changed, the name of the attribute that
        changed, the new value of that attribute, and the name onto 
        which the value should be applied.

        """
        return self._name_inverter

