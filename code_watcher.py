import types
from enaml.core.byteplay import (
    Code, LOAD_ATTR, LOAD_CONST, ROT_TWO, DUP_TOP, CALL_FUNCTION, POP_TOP,
    LOAD_FAST, STORE_FAST, BUILD_TUPLE, ROT_THREE, UNPACK_SEQUENCE, DUP_TOPX,
    BINARY_SUBSCR, GET_ITER, LOAD_NAME, LOAD_GLOBAL, DELETE_NAME, DELETE_GLOBAL
)


class Watcher(object):

    def load_name(self, name):
        print 'load name', name

    def call_function(self, func, args, kwargs):
        print 'call function', args, kwargs

    def get_item(self, obj, index):
        print 'get item', obj, index

    def get_attr(self, obj, attr):
        print 'get attr', obj, attr


def translate_code(code, f_globals):
    bp_code = Code.from_code(code)
    code_list = list(bp_code.code)

    # Make a first pass over the code list and replace LOAD_GLOBAL with
    # LOAD_NAME. This enables dynamic scoping using a custom locals map.
    for idx, (op, op_arg) in enumerate(code_list):
        if op == LOAD_GLOBAL:
            code_list[idx] = (LOAD_NAME, op_arg)
        if op == DELETE_GLOBAL:
            code_list[idx] = (DELETE_NAME, op_arg)

    # The list of code segments that will be inserted into the
    # new bytecode for the expression.
    inserts = []
    for idx, (op, op_arg) in enumerate(code_list):
        # This bit of code is injected between the object on TOS
        # and its pending attribute access. The TOS obj is duped,
        # the rotated above the binder code. The attr is loaded,
        # and the binder is called with the object and attr. The
        # return value of the binder is discarded. This leaves the
        # original TOS and pending attribute access to continue on
        # as normal
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
            inserts.append((idx, code))
        elif op == CALL_FUNCTION:
            # This computes the number of objects on the stack
            # between TOS and the object being called. Only the
            # last 16bits of the op_arg are signifcant. The lowest
            # 8 are the number of positional args on the stack,
            # the upper 8 is the number of kwargs. For kwargs, the
            # number of items on the stack is twice this number
            # since the values on the stack alternate name, value.
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
            inserts.append((idx, code))
        elif op == BINARY_SUBSCR:
            code = [                            # obj -> idx
                (DUP_TOPX, 2),                  # obj -> idx -> obj -> idx -> tracer
                (LOAD_FAST, '_[tracer]'),       # obj -> idx -> obj -> idx -> tracer
                (LOAD_ATTR, 'binary_subscr'),   # obj -> idx -> obj -> idx -> tracefunc
                (ROT_THREE, None),              # obj -> idx -> tracefunc -> obj -> idx
                (CALL_FUNCTION, 0x0002),        # obj -> idx -> retval
                (POP_TOP, None),                # obj -> idx
            ]
            inserts.append((idx, code))
        elif op == GET_ITER:
            code = [                        # obj
                (DUP_TOP, None),            # obj -> obj
                (LOAD_FAST, '_[tracer]'),   # obj -> obj -> tracer
                (LOAD_ATTR, 'get_iter'),    # obj -> obj -> tracefunc
                (ROT_TWO, None),            # obj -> tracefunc -> obj
                (CALL_FUNCTION, 0x0001),    # obj -> retval
                (POP_TOP, None),            # obj
            ]
            inserts.append((idx, code))
        elif op == LOAD_NAME:
            code = [                        #
                (LOAD_FAST, '_[tracer]'),   # tracer
                (LOAD_ATTR, 'load_name'),   # tracefunc
                (LOAD_CONST, op_arg),       # tracefunc -> name
                (CALL_FUNCTION, 0x0001),    # retval
                (POP_TOP, None),            #
            ]
            inserts.append((idx, code))

    insertions = {}
    for idx, code in inserts:
        insertions[idx] = code

    # Create a new code list which interleaves the code generated
    # by the monitors at the appropriate location in the expression.
    new_code = []
    for idx, code_op in enumerate(code_list):
        if idx in insertions:
            new_code.extend(insertions[idx])
        new_code.append(code_op)

    bp_code.code = new_code
    bp_code.newlocals = False
    bp_code.args = ('_[tracer]',) + bp_code.args
    eval_code = bp_code.to_code()

    return types.FunctionType(eval_code, f_globals)


class CustomScope(dict):

    def __init__(self, f_globals):
        self._f_globals = f_globals

    def __getitem__(self, name):
        print
        print '############# getitem', name
        print
        try:
            r = self._f_globals[name]
        except KeyError:
            r = getattr(__builtins__, name)
        return r

    def __setitem__(self, name, value):
        print
        print '############ setitem', name, value
        print
        self._f_globals[name] = value

    def __delitem__(self, name):
        print
        print '############ delitem', name
        print
        del self._f_globals[name]


class CodeTracer(object):

    def __init__(self, code, f_globals):
        self._s = CustomScope(f_globals)
        self._watchers = []
        self._func = translate_code(code, self._s)

    def __call__(self, watcher, *args, **kwargs):
        self._watchers.append(watcher)
        try:
            self._func(self, *args, **kwargs)
        finally:
            self._watchers.pop()

    def load_name(self, name):
        print 'load_name', name

    def load_attr(self, obj, attr):
        print 'load attr', obj, attr

    def call_function(self, func, arg_tuple, nargs):
        print 'call function', func, arg_tuple

    def binary_subscr(self, obj, idx):
        print 'binary subscr', type(obj), idx

    def get_iter(self, obj):
        print 'get iter', obj


class Foo(object):
    def __init__(self, *args, **kwargs): pass
    a = 1
    b = 2
    c = 3


foobar = 12

def tester():
    f = Foo()
    Bar = Foo
    c = (f.a, f.b, f.c, f)
    c[-1].a
    fs = [Bar(1, 2, w=12) for i in range(10)]
    d = [f.b for f in fs]
    del f
    del c
    #global foobar
    del foobar



if __name__ == '__main__':
    t = CodeTracer(tester.func_code, tester.func_globals)
    import dis
    print dis.dis(t._func)
    t(None)
    print foobar
