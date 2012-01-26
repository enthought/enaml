#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from abc import ABCMeta, abstractmethod
import weakref

from traits.api import HasTraits, Disallow

from .parsing import byteplay as bp


#------------------------------------------------------------------------------
# Notification Handling
#------------------------------------------------------------------------------
class NotificationEvent(object):
    """ An event object passed to the callback of a NotifierProxy, it
    contains information about the emitter of the notification and any
    metadata that the emitter wishes to pass to the receiver.

    """
    __slots__ = ('emitter', 'metadata')

    def __init__(self, emitter, **metadata):
        """ Initialize a notifier event.

        Parameters
        ----------
        emitter : object
            The object which emitted this event.
        
        **metadata
            Any other information that the emitter wishes to make 
            available to the receiver.

        """
        self.emitter = emitter
        self.metadata = metadata


class WeakSentinel(object):
    """ An object which is simply weak-refable but serves to disconnect
    notifiers when a reset is requested.

    """
    __slots__ = ('__weakref__')


class NotifierProxy(object):
    """ An object which allows a strong callback to be registered weakly
    with notifiers, without the notifiers requiring knowledge of the
    callback.

    """
    __slots__ = ('_callback', '_sentinel')

    def __init__(self, callback):
        """ Initialize a WeakNotifier.

        Parameters
        ----------
        callback : callable
            A callable which takes a single argument, a NotifierEvent, 
            and which is called whenever any of its notifiers change.
            A strong reference is maintained to the callback.

        """
        self._callback = callback
        self._sentinel = weakref.ref(WeakSentinel())
    
    def reset(self):
        """ Reset this proxy so that any existing notifiers drop their
        connections and no longer trigger notifications until the next 
        time they are connected. This will typically be called by the
        subscriber.

        """
        self._sentinel = weakref.ref(WeakSentinel())

    def notify(self, notifier_event):
        """ Notify the external subscriber that an event has occurred.
        This will typically be called by the notifiers.

        Parameters
        ----------
        notifier_event : NotificationEvent
            The NotificationEvent instance to pass to the subscriber.

        """
        self._callback(notifier_event)

    def disconnector(self):
        """ Returns an internal object which is stored weakly. This 
        object is destroyed whenever a reset of the proxy is requested. 
        Consumers of this notifier should use a weak reference to this 
        object to connect a callback which will destroy any notifiers 
        they may have previously created when the disconnector dies.

        """
        return self._sentinel


#------------------------------------------------------------------------------
# Abstract Monitor
#------------------------------------------------------------------------------
class AbstractMonitor(object):
    """ An abstract base class which defines the api for implementing 
    an expression monitor. 

    An expression Monitor is responsible for generating bytecode which
    will be inserted into a Python expression and which inspects the
    Python stack during the evaluation to determine if it is appropriate
    to attach some form of notifier to the constiuents. If a notifier is 
    warranted, it should make the appropriate connections and call the
    notify method on the provided notifier object.

    """
    __metaclass__ = ABCMeta

    def __init__(self, notifier):
        """ Initialize a monitor instance.

        Parameters
        ----------
        notifier : NotifierProxy
            A NotifierProxy object which should be used to connect any 
            necessary notifiers of the monitor.

        """
        self.notifier = notifier

    @abstractmethod
    def get_insertion_code(self, code_list):
        """ Generates the byteplay code operations to be inserted into 
        the expression code object in order to monitor execution.

        Parameters
        ----------
        code_list : list of (op_code, op_arg)
            The list of byteplay code operations for the expression.
            If no code need be generated, an empty list should be 
            returned.

        Returns
        -------
        result : list of (insertion_idx, code_ops)
            A list of 2-tuples where the first item is an integer index
            into the original code_list and the second item is the list
            of byteplay code operations to insert into the final code.

        Notes
        -----
            The generated instertion code *must* have a net-zero effect
            on the Python stack. This means that the inserted code should
            leave the stack exactly the way it found it. If this is not
            maintained, then random exceptions and/or crashes *will*
            result.

        """
        raise NotImplementedError


#------------------------------------------------------------------------------
# Abstract Attribute Monitor
#------------------------------------------------------------------------------
class AbstractAttributeMonitor(AbstractMonitor):
    """ An abstract monitor which monitors the expression evaluation for 
    attribute access and calls a method with the object and attribute 
    which is being accessed.
    
    """
    def get_insertion_code(self, code_list):
        """ Generates the byteplay code operations to be inserted into 
        the expression code object to monitor attribute accesses. When
        an attribute access occurs, the 'monitor_attribute' method will 
        be called with the object and attribute name as arguments.

        Parameters
        ----------
        code_list : list of (op_code, op_arg)
            The list of byteplay code operations for the expression.
            If no code need be generated, an empty list should be 
            returned.

        Returns
        -------
        result : list of (insertion_idx, code_ops)
            A list of 2-tuples where the first item is an integer index
            into the original code_list and the second item is the list
            of byteplay code operations to insert into the final code.

        Notes
        -----
            The generated instertion code *must* have a net-zero effect
            on the Python stack. This means that the inserted code should
            leave the stack exactly the way it found it. If this is not
            maintained, then random exceptions and/or crashes *will*
            result.

        """
        # A weakref to this instance which is used by the closure
        # injected into the bytecode for this monitor.
        wr_self = weakref.ref(self)

        # A weak closure which is injected into the stack to call the
        # monitor method upon attribute access.
        def code_binder(obj, attr):
            this = wr_self()
            if this is not None:
                this.monitor_attribute(obj, attr)
        
        # The list of code segments that will be inserted into the
        # new bytecode for the expression.
        insertion_code = []

        for idx, (op, op_arg) in code_list:
            # This bit of code is injected between the object on TOS
            # and its pending attribute access. The TOS obj is duped,
            # the rotated above the binder code. The attr is loaded,
            # and the binder is called with the object and attr. The
            # return value of the binder is discarded. This leaves the
            # original TOS and pending attribute access to continue on
            # as normal
            if op == bp.LOAD_ATTR:
                code = [
                    (bp.DUP_TOP, None),
                    (bp.LOAD_CONST, code_binder),
                    (bp.ROT_TWO, None),
                    (bp.LOAD_CONST, op_arg),
                    (bp.CALL_FUNCTION, 0x0002),
                    (bp.POP_TOP, None),
                ]
                insertion_code.append((idx, code))

        return insertion_code

    @abstractmethod
    def monitor_attribute(self, obj, attr):
        """ Hooks up any necessary monitors for the given object and 
        attribute. 

        Parameters
        ----------
        obj : object
            The object on which the attribute access is being performed.
        
        attr : string
            The name of the attribute which is being accessed on the
            object.
        
        """
        raise NotImplementedError


#------------------------------------------------------------------------------
# Abstract Call Monitor
#------------------------------------------------------------------------------
class AbstractCallMonitor(AbstractMonitor):
    """ An abstract monitor which monitors the expression evaluation for 
    function calls and calls a method with the object and arguments which
    are being called.
    
    """
    def get_insertion_code(self, code_list):
        """ Generates the byteplay code operations to be inserted into 
        the expression code object to monitor function calls. When an
        attribute access occurs, the 'monitor_function' method will be 
        called with the object, args, and kwargs.

        Parameters
        ----------
        code_list : list of (op_code, op_arg)
            The list of byteplay code operations for the expression.
            If no code need be generated, an empty list should be 
            returned.

        Returns
        -------
        result : list of (insertion_idx, code_ops)
            A list of 2-tuples where the first item is an integer index
            into the original code_list and the second item is the list
            of byteplay code operations to insert into the final code.

        Notes
        -----
            The generated instertion code *must* have a net-zero effect
            on the Python stack. This means that the inserted code should
            leave the stack exactly the way it found it. If this is not
            maintained, then random exceptions and/or crashes *will*
            result.

        """
        # A weakref to this instance which is used by the closures
        # injected into the bytecode for this monitor.
        wr_self = weakref.ref(self)

        # A weak closure which is injected into the stack to call the
        # monitor method on function call.
        def code_binder(func_obj, arg_tuple, arg_spec):
            if callable(func_obj):
                this = wr_self()
                if this is not None:
                    nargs = arg_spec & 0xFF
                    args = arg_tuple[:nargs]
                    kwargs = dict(zip(arg_tuple[nargs:], arg_tuple[nargs+1:]))
                    this.monitor_function(func_obj, args, kwargs)
            return (func_obj, arg_tuple)
                
        # The list of code segments that will be inserted into the
        # new bytecode for the expression.
        insertion_code = []

        for idx, (op, op_arg) in code_list:
            # This bit of code is injected just before a function call
            # is performed. The arguments on the stack are packed into
            # tuple. The code binder is then pushed onto the stack and
            # rotated under the func_obj and arg_tuple. The arg spec
            # is then loaded and the code binder is invoked. The return 
            # value of the code binder is the original func_obj and 
            # arg_tuple. This return tuple is unpacked, and then the 
            # arg_tuple is unpacked and the function call proceeds as 
            # normal.
            if op == bp.CALL_FUNCTION:
                # This computes the number of objects on the stack 
                # between TOS and the object being called. Only the
                # last 16bits of the op_arg are signifcant. The lowest
                # 8 are the number of positional args on the stack,
                # the upper 8 is the number of kwargs. For kwargs, the
                # number of items on the stack is twice this number 
                # since the values on the stack alternate name, value.
                n_stack_args = (op_arg & 0xFF) + 2 * ((op_arg >> 8) & 0xFF)
                code = [
                    (bp.BUILD_TUPLE, n_stack_args),
                    (bp.LOAD_CONST, code_binder),
                    (bp.ROT_THREE, None),
                    (bp.LOAD_CONST, op_arg),
                    (bp.CALL_FUNCTION, 0x0003),
                    (bp.UNPACK_SEQUENCE, 2),
                    (bp.UNPACK_SEQUENCE, n_stack_args),
                ]
                insertion_code.append((idx, code))
            
            # TODO - CALL_FUNCTION_VAR, CALL_FUNCTION_KW, CALL_FUNCTION_VAR_KW

        return insertion_code
    
    @abstractmethod
    def monitor_function(self, func_obj, args, kwargs):
        """ Hooks up any necessary monitors for the given function object
        and the args and kwargs with which it is being called.

        Parameters
        ----------
        func_obj : callable object
            The function-like object which is being called.
        
        args : tuple
            The arguments being passed to the function.

        kwargs : dict
            The keyword arguments being passed to the function.
        
        """
        raise NotImplementedError


#------------------------------------------------------------------------------
# Trait Attribute Monitor
#------------------------------------------------------------------------------
class TraitAttributeMonitor(AbstractAttributeMonitor):
    """ An AbstractAttributeMonitor implementation which binds listeners
    to trait attributes on HasTraits classes.

    """
    def __init__(self, *args, **kwargs):
        super(TraitAttributeMonitor, self).__init__(*args, **kwargs)

        # When passing a bound method to on_trait_change, traits will
        # ignore the 'target' argument and instead build a weak ref
        # to the bound method. To avoid that, we create this weak
        # closure which will call the notifier for us, but it itself 
        # not a bound method and so can be disconnected with a 'target'.
        wr_self = weakref.ref(self)
        def handler(obj, name, old, new):
            this = wr_self()
            if this is not None:
                event = NotificationEvent(
                    self, obj=obj, name=name, old=old, new=new,
                )
                this.notifier.notify(event)
        
        # The notification handler that is used for binding any trait
        # change handlers necessary for the expression.
        self.notification_handler = handler

    def monitor_attribute(self, obj, attr):
        """ Hooks up any necessary trait change notifiers for the given
        object and attribute. 

        Parameters
        ----------
        obj : object
            The object on which the attribute access is being performed.
        
        attr : string
            The name of the attribute which is being accessed on the
            object.
        
        """
        if isinstance(obj, HasTraits):
            # Only hook up a notifier if the attribute access refers
            # to a proper trait. We check for Disallow trait types 
            # since those can be returned by instances of HasStrictTraits
            trait = obj.trait(attr)
            if trait is not None and trait.trait_type is not Disallow:
                handler = self.notification_handler
                target = self.notifier.disconnector()
                obj.on_trait_change(handler, attr, target=target)


#------------------------------------------------------------------------------
# Trait Getattr Monitor
#------------------------------------------------------------------------------
class TraitGetattrMonitor(AbstractCallMonitor):
    """ An AbstractCallMonitor implementation which binds listeners
    to trait attributes on HasTraits classes which are accessed via
    getattr.

    """
    def __init__(self, *args, **kwargs):
        super(TraitGetattrMonitor, self).__init__(*args, **kwargs)

        # When passing a bound method to on_trait_change, traits will
        # ignore the 'target' argument and instead build a weak ref
        # to the bound method. To avoid that, we create this weak
        # closure which will call the notifier for us, but it itself 
        # not a bound method and so can be disconnected with a 'target'.
        wr_self = weakref.ref(self)
        def handler(obj, name, old, new):
            this = wr_self()
            if this is not None:
                event = NotificationEvent(
                    self, obj=obj, name=name, old=old, new=new,
                )
                this.notifier.notify(event)
        
        # The notification handler that is used for binding any trait
        # change handlers necessary for the expression.
        self.notification_handler = handler

    def monitor_function(self, func_obj, args, kwargs):
        """ Hooks up any necessary trait change notifiers for the given
        call to getattr

        Parameters
        ----------
        func_obj : callable object
            The function-like object which is being called. If this is
            not the builtin getattr, or if the call spec is invalid for
            getattr, this method is a no-op.
        
        args : tuple
            The arguments being passed to the function.

        kwargs : dict
            The keyword arguments being passed to the function.
        
        """
        n_args = len(args)
        if func_obj is not getattr or n_args < 2 or n_args > 3 or kwargs:
            return
        
        obj, attr = args[0], args[1]
        if not isinstance(attr, basestring):
            return

        if isinstance(obj, HasTraits):
            # Only hook up a notifier if the attribute access refers
            # to a proper trait. We check for Disallow trait types 
            # since those can be returned by instances of HasStrictTraits
            trait = obj.trait(attr)
            if trait is not None and trait.trait_type is not Disallow:
                handler = self.notification_handler
                target = self.notifier.disconnector()
                obj.on_trait_change(handler, attr, target=target)

