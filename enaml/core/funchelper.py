#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from ctypes import pythonapi, py_object, POINTER, c_int, byref
from types import FunctionType


PyEval_EvalCodeEx = pythonapi.PyEval_EvalCodeEx
PyEval_EvalCodeEx.restype = py_object
PyEval_EvalCodeEx.argtypes = [
    py_object,              # code object
    py_object,              # globals dict
    py_object,              # locals mapping
    POINTER(py_object),     # args array
    c_int,                  # num args
    POINTER(py_object),     # keywords array
    c_int,                  # num keywords
    POINTER(py_object),     # defaults array
    c_int,                  # num defaults
    py_object,              # closure
]


def call_func(func, args, kwargs, f_locals=None):
    """ Call a function which has been modified by the Enaml compiler
    to support tracing and dynamic scoping.

    Parameters
    ----------
    func : types.FunctionType
        The Python function to call.

    args : tuple
        The tuple of arguments to pass to the function.

    kwargs : dict
        The dictionary of keywords to pass to the function.

    f_locals : mapping, optional
        An optional locals mapping to use with the function.

    Returns
    -------
    result : object
        The result of calling the function.

    """
    if not isinstance(func, FunctionType):
        raise TypeError('function must be a Python function')

    if not isinstance(args, tuple):
        raise TypeError('arguments must be a tuple')

    if not isinstance(kwargs, dict):
        raise TypeError('keywords must be a dict')

    if f_locals is not None and not hasattr(f_locals, '__getitem__'):
        raise TypeError('locals must be a mapping')

    defaults = func.func_defaults
    num_defaults = len(defaults) if defaults else 0

    if kwargs:
        keywords = []
        for key, value in kwargs.iteritems:
            keywords.append(key)
            keywords.append(value)
        keywords = tuple(keywords)
        num_keywords = len(keywords) / 2
    else:
        keywords = None
        num_keywords = 0

    args_ptr = byref(py_object(args[0])) if args else None
    defaults_ptr = byref(py_object(defaults[0])) if defaults else None
    keywords_ptr = byref(py_object(keywords[0])) if keywords else None

    result = PyEval_EvalCodeEx(
        func.func_code,
        func.func_globals,
        f_locals,
        args_ptr,
        len(args),
        keywords_ptr,
        num_keywords,
        defaults_ptr,
        num_defaults,
        func.func_closure
    )

    return result


# Use the faster version of `call_func` if it's available.
try:
    from enaml.extensions.funchelper import call_func
except ImportError:
    pass

