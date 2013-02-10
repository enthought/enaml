#------------------------------------------------------------------------------
#  Copyright (c) 2013, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
""" A pure Python implementation of the observerpool.cpp extension.

This exists to make Enaml usable without a C++ compiler. However, it is
much slower than the extension, and production deployments should use
Enaml with the compiled extension modules for the best performance.

"""
class _Topic(object):
    """ A private class used by `ObserverPool`.

    """
    __slots__ = ('_topic', '_observers', '_tasks')

    def __init__(self, topic):
        self._topic = topic
        self._observers = []
        self._tasks = None

    def add_observer(self, observer):
        tasks = self._tasks
        if tasks is not None:
            tasks.append(lambda: self.add_observer(observer))
            return
        observers = self._observers
        if observer not in observers:
            observers.append(observer)

    def remove_observer(self, observer):
        tasks = self._tasks
        if tasks is not None:
            tasks.append(lambda: self.remove_observer(observer))
            return
        observers = self._observers
        if observer in observers:
            observers.remove(observer)

    def notify_observers(self, argument):
        owns_tasks = self._tasks is None
        if owns_tasks:
            self._tasks = []
        try:
            for observer in self._observers:
                if observer:
                    observer(argument)
                else:
                    self._tasks.append(lambda: self.remove_observer(observer))
        finally:
            if owns_tasks:
                tasks = self._tasks
                self._tasks = None
                for task in tasks:
                    task()


class ObserverPool(object):
    """ The `ObserverPool` class used by `Observable`.

    There is a much higher performance version of this class available
    as a C++ extension. Prefer building Enaml with this extension.

    An `ObserverPool` will invoke its callables in the order in which
    they were added. Before an observer is invoked, it will be tested
    for boolean truth. If it tests False, it will be removed from the
    pool. This mechanism is designed to reduce the number of weakrefs
    required to automatically remove an observer. An observer which
    needs to be removed should just change its boolean state to False
    and wait until the next dispatch cycle to be removed.

    """
    __slots__ = ('_topics',)

    def __init__(self):
        """ Initialize an ObserverPool.

        """
        self._topics = []

    def add_observer(self, topic, observer):
        """ Add an observer to the pool for the given topic.

        Parameters
        ----------
        topic : str
            The topic to which the observer should be notified.

        observer : callable
            A callable which accepts a single argument. The callable
            will be invoked whenever the given topic is notified. A
            given callable will be added at most once per topic.

        """
        for t in self._topics:
            if t._topic == topic:
                t.add_observer(observer)
                return
        else:
            t = _Topic(topic)
            t.add_observer(observer)
            self._topics.append(t)

    def remove_observer(self, topic, observer):
        """ Remove an observer from the pool for the given topic.

        topic : str
            The topic for which the observer should be removed.

        observer : callable
            The observer to remove from the pool.

        """
        for t in self._topics:
            if t._topic == topic:
                t.remove_observer(observer)
                return

    def notify_observers(self, topic, argument):
        """ Notify the observers listening to a topic.

        Parameters
        ----------
        topic : str
            The topic for which observers should be notified.

        argument : object
            The argument to pass to the observers.

        """
        for t in self._topics:
            if t._topic == topic:
                t.notify_observers(argument)
                return


#: Use the faster C++ version if available
try:
    from enaml.extensions.observerpool import ObserverPool
except ImportError:
    pass

