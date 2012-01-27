#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from ..toolkit import Toolkit
from ..exceptions import EnamlRuntimeError

#------------------------------------------------------------------------------
# Instructions
#------------------------------------------------------------------------------
(
    # Load the given symbol from the global namespace and push it onto 
    # the stack following proper Enaml scope resolution semantics
    LOAD_GLOBAL,

    # Load the given symbol from the local namespace and push it onto 
    # the stack
    LOAD_LOCAL,

    # Push the given value onto the stack
    LOAD_CONST,

    # Replace the top of the stack with getattr(tos, op_arg)
    LOAD_ATTR,

    # Replace the top of the stack with the tos[op_arg]
    GET_ITEM,

    # Load the globals closure onto the stack
    LOAD_GLOBALS_CLOSURE,

    # Load the locals closure onto the stack
    LOAD_LOCALS_CLOSURE,

    # Store the top of the stack as a local in *name*
    STORE_LOCAL,

    # The tos is a code object, eval it in the proper scopes and
    # push the results onto the stack
    EVAL,

    # op_arg is (n_args, n_kwargs) where each kwarg is two slots
    # for name and value. The stack order is (top of stack to right):
    # | callable | arg_1 | arg_n | name_1 | kwarg_1 | name_n | kwarg_n
    CALL,

    # op_arg in the same as for CALL but ENAML_CALL is a special
    # op code for handling calls that will create Enaml widgets
    # the return value of this call is a tuple of (widgets, ns)
    # where widgets is a sequence and ns is a dict.
    ENAML_CALL,

    # Unpack top of stack into *count* individual values placed on the 
    # stack right-to-left
    UNPACK_SEQUENCE,

    # Pop the top two elements of the stack. The first pop are the 
    # children to add to the parent. The second pop is the parent.
    ENAML_ADD_CHILDREN,

    # Duplicate the top of the stack
    DUP_TOP,

    # Pop the top of the stack and discard
    POP_TOP,

    # replace tos with iter(tos)
    GET_ITER,

    # tos is iterable, this calls the .next() method. If it yields a 
    # value, the value is pushed onto the stack. Otherwise, the empty
    # iterator is popped and we jump to the instruction number op_arg
    FOR_ITER,

    # jump to the op_arg instruction index
    JUMP_ABSOLUTE,

    # rotate the top two items in the stack
    ROT_TWO,

) = range(19)


class _NullComponent(object):
    """ A null component class used to prime the vm stack before
    executing any instructions. This alleviates the need to special
    case for an empty stack anywhere.

    """
    __slots__ = ('children',)

    def __init__(self):
        self.children = []
    
    def add_child(self, child):
        self.children.append(child)


def evalcode(instructions, global_ns, local_ns):
    """ The main eval loop of the Enaml virtual machine.

    Arguments
    ---------
    instructions : list
        The list of (op, op_arg) instructions to execute.
    
    global_ns : dict
        The global namespace dictionary to use for execution.
    
    local_ns : mapping
        The local namespace mapping type to use for execution.
    
    Returns
    -------
    results : sequence
        A sequence of instantiated and populated components.
    
    """
    # Prime the stack with a null component as a performance tweak 
    # which prevents the need to ever test for an empty stack.
    # Also, store a reference to the bound list methods so that they
    # do not need to be continuously recreated during the eval loop.
    stack = [(_NullComponent(),)]
    push = stack.append
    pop = stack.pop

    # Because of limitations on the flexibility of Python scoping,
    # it is incredibly difficult to inject a middle scope between
    # globals() and __builtins__ which is where we want our toolkit
    # scope to live. So a safe (albeit a bit slow) workaround is 
    # to create a closure with the scopes in which we're interested,
    # and collapse them on demand just before use. This allows behavior
    # such as changing module variables to work properly. Its only
    # necessary to perform the collapse when using eval or exec. When
    # we control the lookup, it's faster to just walk the scope chain
    # directly (see the LOAD_GLOBAL handler)
    active_toolkit = Toolkit.active_toolkit()

    # Collapse the global scope into a single dictionary that looks
    # up in the order of globals -> toolkit -> __builtins__
    def globals_closure():
        f_globals = {}
        update = f_globals.update
        update(active_toolkit)
        update(global_ns)
        return f_globals
    
    # Since eval and exec accept a mapping type for a locals object
    # we don't need to collapse anything since such behavior can be
    # implemented via __getitem__
    def locals_closure():
        return local_ns

    # The instruction index variables. Jump op code handlers
    # directly manipulate the idx variable.
    max_idx = len(instructions)
    idx = 0

    # The enaml eval loop
    while idx < max_idx:

        op, op_arg = instructions[idx]

        # Push globals_closure()[op_arg]
        if op == LOAD_GLOBAL:
            try:
                obj = global_ns[op_arg]
            except KeyError:
                try:
                    obj = active_toolkit[op_arg]
                except KeyError:
                    try:
                        obj = __builtins__[op_arg]
                    except KeyError:
                        raise NameError('name `%s` is not defined' % op_arg)
            push(obj)
            
        # Push locals_closure()[op_arg]
        elif op == LOAD_LOCAL:
            try:
                obj = local_ns[op_arg]
            except KeyError:
                raise NameError('name `%s` is not defined' % op_arg)
            push(obj)

        # Push op_arg
        elif op == LOAD_CONST:
            push(op_arg)

        # Replace TOS with getattr(TOS, op_arg)
        elif op == LOAD_ATTR:
            obj = pop()
            push(getattr(obj, op_arg))
        
        # Replace TOS with TOS[idx]
        elif op == GET_ITEM:
            obj = pop()
            push(obj[op_arg])

        # Push globals_closure
        elif op == LOAD_GLOBALS_CLOSURE:
            push(globals_closure)
        
        # Push locals_closure
        elif op == LOAD_LOCALS_CLOSURE:
            push(locals_closure)

        # Store TOS as locals_ns[op_arg] = TOS
        elif op == STORE_LOCAL:
            obj = pop()
            local_ns[op_arg] = obj
        
        # Replace TOS with eval(TOS, globals_closure(), locals_closure())
        elif op == EVAL:
            code = pop()
            f_globals = globals_closure()
            f_locals = locals_closure()
            push(eval(code, f_globals, f_locals))
        
        # op_arg is (n_args, n_kwargs)
        # stack order is | ... | obj | args... | kwargs... |(TOS)
        # Replace TOS with obj(*args, **kwargs)
        elif op == CALL:
            n_args, n_kwargs = op_arg
            kwargs = {}
            for _ in range(n_kwargs):
                value = pop()
                key = pop()
                kwargs[key] = value
            # arguments get pushed on the stack left to right, so they 
            # pop off in the reverse order. The need to be reversed 
            # again before they can be passed to the call.
            args = [pop() for _ in range(n_args)]
            args.reverse()
            obj = pop()
            results = obj(*args, **kwargs)
            push(results)

        # stack state here is the same as CALL, but,
        # we do obj.__enaml_call__(*args, **kwargs) which 
        # returns two items. We push each item individually.
        # We could do this with an additional UNPACK_SEQUENCE
        # operation, but this is a simple performance tweak.
        elif op == ENAML_CALL:
            n_args, n_kwargs = op_arg
            kwargs = {}
            for _ in range(n_kwargs):
                value = pop()
                key = pop()
                kwargs[key] = value
            args = [pop() for _ in range(n_args)]
            args.reverse()
            obj = pop()
            sequence, ns = obj.__enaml_call__(*args, **kwargs)
            push(sequence)
            push(ns)

        # Replace TOS with unpacked items
        elif op == UNPACK_SEQUENCE:
            # op_arg is always >= 1
            #
            # If it's > 1 we unpack that many args with length checking
            #
            # If it == 1, we unpack the sequence only if the sequence
            # length is one. Otherwise we push the whole thing back.
            sequence = pop()
            if op_arg > 1:
                n_elems = len(sequence)
                if n_elems == op_arg:
                    for elem in reversed(sequence):
                        push(elem)
                elif n_elems > op_arg:
                    raise ValueError('too many values to unpack')
                else:
                    msg = 'need more than %s values to unpack' % n_elems
                    raise ValueError(msg)
            else:
                if len(sequence) == 1:
                    push(sequence[0])
                else:
                    push(sequence)

        # Add the children to the their parent.
        # The parent item is the sequence of widgets created by the
        # previous __enaml_call__. If that sequence has a length
        # greater than 1, we don't know to which item we should add
        # the children.
        elif op == ENAML_ADD_CHILDREN:
            children = pop()
            parent = pop()
            if len(parent) > 1:
                raise EnamlRuntimeError('Cannot add children to a sequence')
            parent = parent[0]
            for child in children:
                parent.add_child(child)

        # Duplicate the TOS
        elif op == DUP_TOP:
            val = pop()
            push(val)
            push(val)

        # Pop the TOS
        elif op == POP_TOP:
            pop()
        
        # Replace TOS with iter(TOS)
        elif op == GET_ITER:
            push(iter(pop()))
        
        # Push TOS.next() if it yields a value, leave iterator
        # in place. Jump to op_arg if .next() raises StopIteration.
        elif op == FOR_ITER:
            obj = pop()
            try:
                val = obj.next()
            except StopIteration:
                idx = op_arg
                continue
            else:
                push(obj)
                push(val)
        
        # Jump to the instruction index given by op_arg
        elif op == JUMP_ABSOLUTE:
            idx = op_arg
            continue

        # Rotate the top two items in the stack
        elif op == ROT_TWO:
            first = pop()
            second = pop()
            push(first)
            push(second)

        else:
            raise ValueError('Invalid VM op')
        
        idx += 1
    
    # Convert the child of the null component to a tuple for
    # processing by our caller.
    return tuple(pop()[0].children), local_ns

