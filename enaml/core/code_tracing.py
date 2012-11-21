#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .byteplay import (
    Code, LOAD_ATTR, LOAD_CONST, ROT_TWO, DUP_TOP, CALL_FUNCTION, POP_TOP,
    LOAD_FAST, BUILD_TUPLE, ROT_THREE, UNPACK_SEQUENCE, DUP_TOPX,
    BINARY_SUBSCR, GET_ITER, LOAD_NAME, LOAD_GLOBAL
)


class CodeTracer(object):
    """ A base class for implementing code tracers.

    This class defines the interface for a code tracer object, which is
    an object which can be passed as the first argument to a code object
    which has been transformed to enable tracing. Methods on the tracer
    are called with relevant arguments from the Python stack, when that
    particular code segment is executing. The return values of a tracer
    method is ignored; exceptions are propagated.

    """
    def load_attr(self, obj, attr):
        """ Called before the LOAD_ATTR opcode is executed.

        Parameters
        ----------
        obj : object
            The object which owns the attribute.

        attr : str
            The attribute being loaded.

        """
        pass

    def call_function(self, func, argtuple, argspec):
        """ Called before the CALL_FUNCTION opcode is executed.

        Parameters
        ----------
        func : object
            The object being called.

        argtuple : tuple
            The argument tuple from the stack (see notes).

        argspec : int
            The argument tuple specification.

        Notes
        -----
        The `argstuple` contains both positional and keyword argument
        information. `argspec` is an int which specifies how to parse
        the information. The lower 16bits of `argspec` are significant.
        The lowest 8 bits are the number of positional arguments which
        are the first n items in `argtuple`. The second 8 bits are the
        number of keyword arguments which follow the positional args in
        `argtuple` and alternate name -> value. `argtuple` can be parsed
        into a conventional tuple and dict with the following:

            nargs = argspec & 0xFF
            args = argtuple[:nargs]
            kwargs = dict(zip(argtuple[nargs::2], argtuple[nargs+1::2]))

        """
        pass

    def binary_subscr(self, obj, idx):
        """ Called before the BINARY_SUBSCR opcode is executed.

        Parameters
        ----------
        obj : object
            The object being indexed.

        idx : object
            The index.

        """
        pass

    def get_iter(self, obj):
        """ Called before the GET_ITER opcode is executed.

        Parameters
        ----------
        obj : object
            The object which should return an iterator.

        """
        pass


class CodeInverter(object):
    """ A base class for implementing code inverters.

    This class defines the interface for a code inverter object, which is
    an object which can be passed as the first argument to a code object
    which has been transformed to enable inversion. The methods on the
    inverter are called with relevant arguments from the Python stack,
    when that particular code segment is executing. The return values of
    a tracer method is ignored; exceptions are propagated.

    The default behavior of an inverter is to raise. Implementations
    must provide their own code.

    """
    def fail(self):
        """ Called by the modified code to raise an inversion exception.

        """
        raise RuntimeError('Cannot assign to the given expression')

    def load_name(self, name, value):
        """ Called before the LOAD_NAME opcode is executed.

        This method should perform a STORE_NAME operation.

        Parameters
        ----------
        name : str
            The name being loaded.

        value : object
            The value to store.

        """
        self.fail()

    def load_attr(self, obj, attr, value):
        """ Called before the LOAD_ATTR opcode is executed.

        This method should perform a STORE_ATTR operation.

        Parameters
        ----------
        obj : object
            The object which owns the attribute.

        attr : str
            The attribute being loaded.

        value : object
            The value to store

        """
        self.fail()

    def call_function(self, func, argtuple, argspec, value):
        """ Called before the CALL_FUNCTION opcode is executed.

        This method should perform an appropriate store operation.

        Parameters
        ----------
        func : object
            The object being called.

        argtuple : tuple
            The argument tuple from the stack (see Notes).

        argspec : int
            The argument tuple specification.

        value : object
            The value to store.

        Notes
        -----
        The semantics of the arguments is identical to the method
        `call_function` on the `CodeTracer` type.

        """
        self.fail()

    def binary_subscr(self, obj, idx, value):
        """ Called before the BINARY_SUBSCR opcode is executed.

        This method should perform a STORE_SUBSCR operation.

        Parameters
        ----------
        obj : object
            The object being indexed.

        idx : object
            The index.

        value : object
            The value to store.

        """
        self.fail()


def transform_code(code, trace):
    """ Transform a code object into a Python function.

    This will disassemble the given code object and rewrite it to enable
    Enaml's dynamic scoping and tracing features.

    Parameters
    ----------
    code : types.CodeType
        The Python code object which should transformed.

    trace : bool
        Whether or not to add tracing code to the function. If this is
        True, the arguments of the returned function are extended so
        that the first argument to the function is a `CodeTracer`
        instance.

    Returns
    -------
    result : types.CodeType
        A Python code object which implements the desired functionality.

    """
    bp_code = Code.from_code(code)
    code_list = list(bp_code.code)

    # Replacing LOAD_GLOBAL with LOAD_NAME enables dynamic scoping by
    # way of a custom locals mapping. There is a C extension module
    # with a function `call_func` which allows a Python function to
    # be called with a locals mapping, which is normally not possible.
    for idx, (op, op_arg) in enumerate(code_list):
        if op == LOAD_GLOBAL:
            code_list[idx] = (LOAD_NAME, op_arg)

    # If tracing code is not required, the transformation is complete.
    if not trace:
        bp_code.code = code_list
        bp_code.newlocals = False
        return bp_code.to_code()

    # This builds a mapping of code idx to a list of ops, which are the
    # tracing bytecode instructions which will be inserted into the code
    # object being transformed. The ops assume that a tracer object is
    # available in the fast locals using a non-clashable name. All of
    # the ops have a net-zero effect on the execution stack. Provided
    # that the tracer has no visible side effects, the tracing is
    # transparent.
    inserts = {}
    for idx, (op, op_arg) in enumerate(code_list):
        if op == LOAD_ATTR:
            code = [                        # obj
                (DUP_TOP, None),            # obj -> obj
                (LOAD_FAST, '_[tracer]'),   # obj -> obj -> tracer
                (LOAD_ATTR, 'load_attr'),   # obj -> obj -> tracefunc
                (ROT_TWO, None),            # obj -> tracefunc -> obj
                (LOAD_CONST, op_arg),       # obj -> tracefunc -> obj -> attr
                (CALL_FUNCTION, 0x0002),    # obj -> retval
                (POP_TOP, None),            # obj
            ]
            inserts[idx] = code
        elif op == CALL_FUNCTION:
            # This computes the number of objects on the stack between
            # TOS and the object being called. Only the last 16bits of
            # the op_arg are signifcant. The lowest 8 are the number of
            # positional args on the stack, the upper 8 is the number of
            # kwargs. For kwargs, the number of items on the stack is
            # twice this number since the values on the stack alternate
            # name, value.
            n_stack_args = (op_arg & 0xFF) + 2 * ((op_arg >> 8) & 0xFF)
            code = [                                # func -> arg(0) -> arg(1) -> ... -> arg(n-1)
                (BUILD_TUPLE, n_stack_args),        # func -> argtuple
                (DUP_TOPX, 2),                      # func -> argtuple -> func -> argtuple
                (LOAD_FAST, '_[tracer]'),           # func -> argtuple -> func -> argtuple -> tracer
                (LOAD_ATTR, 'call_function'),       # func -> argtuple -> func -> argtuple -> tracefunc
                (ROT_THREE, None),                  # func -> argtuple -> tracefunc -> func -> argtuple
                (LOAD_CONST, op_arg),               # func -> argtuple -> tracefunc -> func -> argtuple -> argspec
                (CALL_FUNCTION, 0x0003),            # func -> argtuple -> retval
                (POP_TOP, None),                    # func -> argtuple
                (UNPACK_SEQUENCE, n_stack_args),    # func -> arg(n-1) -> arg(n-2) -> ... -> arg(0)
                (BUILD_TUPLE, n_stack_args),        # func -> reversedargtuple
                (UNPACK_SEQUENCE, n_stack_args),    # func -> arg(0) -> arg(1) -> ... -> arg(n-1)
            ]
            inserts[idx] = code
        elif op == BINARY_SUBSCR:
            code = [                            # obj -> idx
                (DUP_TOPX, 2),                  # obj -> idx -> obj -> idx
                (LOAD_FAST, '_[tracer]'),       # obj -> idx -> obj -> idx -> tracer
                (LOAD_ATTR, 'binary_subscr'),   # obj -> idx -> obj -> idx -> tracefunc
                (ROT_THREE, None),              # obj -> idx -> tracefunc -> obj -> idx
                (CALL_FUNCTION, 0x0002),        # obj -> idx -> retval
                (POP_TOP, None),                # obj -> idx
            ]
            inserts[idx] = code
        elif op == GET_ITER:
            code = [                        # obj
                (DUP_TOP, None),            # obj -> obj
                (LOAD_FAST, '_[tracer]'),   # obj -> obj -> tracer
                (LOAD_ATTR, 'get_iter'),    # obj -> obj -> tracefunc
                (ROT_TWO, None),            # obj -> tracefunc -> obj
                (CALL_FUNCTION, 0x0001),    # obj -> retval
                (POP_TOP, None),            # obj
            ]
            inserts[idx] = code

    # Create a new code list which interleaves the generated code with
    # the original code at the appropriate location.
    new_code = []
    for idx, code_op in enumerate(code_list):
        if idx in inserts:
            new_code.extend(inserts[idx])
        new_code.append(code_op)

    # Create the new code object which takes a tracer as the first arg.
    bp_code.code = new_code
    bp_code.newlocals = False
    bp_code.args = ('_[tracer]',) + bp_code.args
    return bp_code.to_code()

