#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
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
        """ Initialize a SchedulerTask.

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
        """ Execute the underlying task. This should only been called
        by the scheduler loop.

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
        """ Unschedule the task so that it will not be executed. If
        the task has already been executed, this call has no effect.

        """
        self.__valid = False

    def result(self):
        """ Returns the result of the task, or ScheduledTask.undefined
        if the task has not yet been executed, was unscheduled before 
        execution, or raised an exception on execution.

        """
        return self.__result


class AbstractTkApplication(object):
    """ A thread safe abstract base class that represents a simple gui
    toolkit application object. It provides convienent abstraction for
    common operations such as creating the toolkit app, starting the 
    event loop, and calling functions on the main gui thread. It also
    provides a priority scheduler which runs tasks on the main gui 
    thread.

    """
    __metaclass__ = ABCMeta

    def __init__(self):
        """ Initialize an AbstractApplication.

        """
        # The heap of pending tasks awaiting processing
        self.__heap = []

        # A never-ending counter that serves to create tie-breakers
        # for heap priority
        self.__counter = count()

        # A Lock which protects access to the heap
        self.__heap_lock = Lock()

    #--------------------------------------------------------------------------
    # Private API 
    #--------------------------------------------------------------------------
    def __process_task(self, task):
        """ Processes the given task, then dispatches the next task.

        """
        task._execute()
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

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def schedule(self, callback, args=None, kwargs=None, priority=50):
        """ Schedule a callable to be executed on the main gui thread 
        according to its priority. This call is thread-safe.

        Parameters
        ----------
        callback : callable
            The callable object to be executed. It must be hashable.

        args : tuple, optional
            The args to pass to the callable.

        kwargs : dict, optional
            The keyword arguments to pass to the callable.

        priority : int, optional
            The priority with which to schedule the callable. The 
            'lowest' priority is 100 and indicates the callable will 
            be placed at the end of the queue. The 'highest' priority
            is 0 and indicates that the callable will jump to the 
            front of the queue. The default is 50.

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
    def initialize(self, *args, **kwargs):
        """ An abstract method which must be implemented by a toolkit
        specific subclass.

        The toolkit implementation of this method should initialize
        an necessary application object and the set the _initialized
        flag to True. It should *not* start the event loop. If the
        application object is already created, it should be a no-op.

        The args and kwargs should be passed, as necessary, to the
        application object constructor.

        """
        raise NotImplementedError
    
    @abstractmethod
    def start_event_loop(self):
        """ An abstract method which must be implemented by a toolkit
        specific subclass.

        The toolkit implementation of this method should start the 
        underlying event loop, or do nothing if it is already started.
        It should raise a RuntimeError if the application object is
        not yet created.

        """
        raise NotImplementedError
    
    @abstractmethod
    def event_loop_running(self):
        """ An abstract method which must be implemented by a toolkit
        specific subclass.

        The toolkit implementation of this method should return True
        if the main event loop is running, False otherwise.

        """
        raise NotImplementedError

    @abstractmethod
    def app_object(self):
        """ An abstract method which must be implemented by a toolkit
        specific subclass.

        The toolkit implementation of this method should return the
        underlying application object, or None if one does not exist.

        """
        raise NotImplementedError

    @abstractmethod    
    def is_main_thread(self):
        """ An abstract method which must be implemented by a toolkit
        specific subclass.

        The toolkit implementation of this method should return True
        if the method was called from the main gui event thread, or
        False otherwise.

        """
        raise NotImplementedError

    @abstractmethod
    def call_on_main(self, callback, *args, **kwargs):
        """ An abstract method which must be implemented by a toolkit
        specific subclass. 

        The toolkit implementation of this method should invoke the 
        given callable in the main gui event thread at some point 
        in the future.

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
        """ An abstract method which must be implemented by a toolkit
        specific subclass. 

        The toolkit implementation of this method should invoke the 
        given callable in the main gui event thread at some point 
        in the future.

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
    def process_events(self):
        """ An abstract method which must be implemented by a toolkit
        specific subclass.

        The toolkit implementation of this method should process all
        pending events in its event queue.

        """
        raise NotImplementedError

