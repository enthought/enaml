#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from abc import ABCMeta, abstractmethod
from heapq import heappush, heappop
from itertools import count
from threading import Lock
    

class ScheduledTask(object):
    """ An object representing a task in the scheduler.

    """
    #: A sentinel object indicating that the result of the task
    #: is undefined or that the task has not yet been executed.
    undefined = object()

    def __init__(self, callback, args, kwargs):
        """ Initialize a ScheduledTask.

        Parameters
        ----------
        callback : callable
            The callable to run when the task is executed.

        args : tuple
            The tuple of positional arguments to pass to the callback.

        kwargs : dict
            The dict of keyword arguments to pass to the callback.

        """
        self.__callback = callback
        self.__args = args
        self.__kwargs = kwargs
        self.__result = self.undefined
        self.__valid = True
        self.__pending = True

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _execute(self):
        """ Execute the underlying task. This should only been called by
        the scheduler loop.

        """
        try:
            if self.__valid:
                self.__result = self.__callback(*self.__args, **self.__kwargs)
        finally:
            self.__pending = False

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def pending(self):
        """ Returns True if this task is pending execution, False
        otherwise.

        """
        return self.__pending

    def unschedule(self):
        """ Unschedule the task so that it will not be executed. If the
        task has already been executed, this call has no effect.

        """
        self.__valid = False

    def result(self):
        """ Returns the result of the task, or ScheduledTask.undefined
        if the task has not yet been executed, was unscheduled before
        execution, or raised an exception on execution.

        """
        return self.__result


class CoreApplication(object):
    """ The abstract base class of Enaml applications. 

    This class implements a large amount of common functionality for 
    managing the messaging around Enaml Object instances. It exposes
    an abstract api which must be implemented by subclasses in order
    to create a fully functional Enaml application.

    """
    __metaclass__ = ABCMeta

    # The singleton application instance
    _instance = None

    @staticmethod
    def instance():
        return CoreApplication._instance

    def __new__(cls, *args, **kwargs):
        if CoreApplication._instance is not None:
            raise RuntimeError('An application instance already exists')
        self = super(CoreApplication, cls).__new__(cls)
        CoreApplication._instance = self
        return self

    def __init__(self, objects=None):
        """ Initialize a CoreApplication.

        """
        # The heap of pending tasks awaiting processing
        self.__heap = []

        # A never-ending counter that serves to create tie-breakers
        # for heap priority
        self.__counter = count()

        # A Lock which protects access to the heap
        self.__heap_lock = Lock()

        # The registered objects being managed by the application.
        self._objects = set()

        register = self.register
        for obj in objects:
            register(obj)

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def __process_task(self, task):
        """ Processes the given task, then dispatches the next task.

        """
        try:
            task._execute()
        finally:
            self.__next_task()
    
    def __next_task(self):
        """ Pulls the next task off the heap and processes it on the 
        main gui thread.

        """
        heap = self.__heap
        with self.__heap_lock:
            if heap:
                priority, count, task = heappop(heap)
                self.call_on_main(self.__process_task, task)

    def _on_object_action(self, object_id, action, content):
        pass

    def register(self, obj):
        objs = self._objects
        if obj not in objs:
            objs.add(obj)
            handler = self._on_object_action
            for _obj in obj.traverse():
                _obj.action.connect(handler)

    def unregister(self, obj):
        objs = self._objects
        if obj in objs:
            objs.remove(obj)
            handler = self._on_object_action
            for _obj in obj.traverse():
                _obj.action.disconnect(handler)

    def snapshot(self):
        return [obj.snapshot() for obj in self._objects]
    
    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def schedule(self, callback, args=None, kwargs=None, priority=0):
        """ Schedule a callable to be executed on the main gui thread.

        This method allows a callback to be scheduled according to a 
        priority. This method is thread-safe.

        Parameters
        ----------
        callback : callable
            The callable object to be executed.

        args : tuple, optional
            The args to pass to the callable.

        kwargs : dict, optional
            The keyword arguments to pass to the callable.

        priority : int, optional
            The priority with which to schedule the callable. The
            lowest priority is 0 and indicates the callable will
            be placed at the end of the queue. There is no highest
            priority.

        Returns
        -------
        result : ScheduledTask
            A task object which can be used to unschedule the task or
            retrieve the results of the callback after the task has
            been executed.

        """
        if args is None:
            args = ()

        if kwargs is None:
            kwargs = {}

        if priority < 0:
            priority = 0

        task = ScheduledTask(callback, args, kwargs)

        heap = self.__heap
        with self.__heap_lock:
            needs_start = len(heap) == 0
            item = (priority, self.__counter.next(), task)
            heappush(heap, item)

        if needs_start:
            self.call_on_main(self.__next_task)
        
        return task

    def has_pending_tasks(self):
        """ Returns True if the scheduler has pending tasks, False
        otherwise.

        """
        with self.__heap_lock:
            has_pending = len(self.__heap) > 0
        return has_pending

    #--------------------------------------------------------------------------
    # Abstract API
    #--------------------------------------------------------------------------
    @abstractmethod
    def call_on_main(self, callback, *args, **kwargs):
        """ An abstract method which must be implemented by a subclass.

        The concrete implementation of this method should invoke the
        given callable in the main event thread at some point in the 
        future.

        Parameters
        ----------
        callback : callable
            The callable object to execute at some point in the future.

        *args
            Any positional arguments to pass to the callback.

        **kwargs
            Any keyword arguments to pass to the callback.

        """
        raise NotImplementedError

    @abstractmethod
    def timer(self, ms, callback, *args, **kwargs):
        """ An abstract method which must be implemented by a subclass.

        The concrete implementation of this method should invoke the
        given callable in the main event thread at the specified time
        in the future.

        Parameters
        ----------
        ms : int
            The number of milliseconds in the future to invoke the 
            callabck.

        callback : callable
            The callable object to execute at some point in the future.

        *args
            Any positional arguments to pass to the callback.

        **kwargs
            Any keyword arguments to pass to the callback.

        """
        raise NotImplementedError
    
    @abstractmethod
    def process_events(self):
        """ An abstract method which must be implemented by a subclass.

        The concrete implementation of this method should process all
        pending events in its event queue.

        """
        raise NotImplementedError

    @abstractmethod
    def start(self):
        """ Start the application.

        """
        raise NotImplementedError

    @abstractmethod
    def stop(self):
        """ Stop the application.

        """
        raise NotImplementedError

