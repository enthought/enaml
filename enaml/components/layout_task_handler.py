#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from collections import deque

from traits.api import HasStrictTraits, Instance

from .abstract_application import ScheduledTask

from ..guard import guard


class LayoutTaskHandler(HasStrictTraits):
    """ A mixin class that provides a basic implementation of layout
    task processing. Subclasses that use the mixin must at least be
    subclasses of BaseComponet and should, in addition, provide a
    freeze() method which returns a context manager, inside which the
    queues will be emptied and the layout handlers called.

    Only classes which actually implement some form of layout handling 
    should inherit this class. Otherwise, layout requests will not
    properly propagate up the widget hierarchy.

    This class should be inherited before the other superclasses of
    the parent class, or the layout handlers will not be properly
    overridden.

    """
    #: A private ScheduledTask that is created when handling requests
    #: for a deferred relayout.
    _relayout_task = Instance(ScheduledTask)
    
    #: A private ScheduledTask that is created when handling requests
    #: for a deferred refresh
    _refresh_task = Instance(ScheduledTask)

    #: A private queue of callables to run in a freeze context before
    #: performing any relayout.
    _relayout_queue = Instance(deque, ())

    #: A private queue of callables to run in a freeze context before
    #: performing any refresh.
    _refresh_queue = Instance(deque, ())

    #--------------------------------------------------------------------------
    # Layout Handling
    #--------------------------------------------------------------------------
    def relayout(self):
        """ A reimplemented parent class method which triggers an update
        of the constraints and a new layout computation. This is called 
        whenever the layout children of the component should have their 
        layout relationships recomputed. The constraints update and 
        relayout occur immediately and are completed before the method 
        returns. If the component is not fully initialized, this is a 
        no-op.

        """
        if not self.initialized:
            return

        # Protect against relayout recursion.
        if not guard.guarded(self, 'relayout'):
            with guard(self, 'relayout'):
                with self.freeze():
                    queue = self._relayout_queue
                    if queue:
                        while queue:
                            callback, args, kwargs = queue.popleft()
                            callback(*args, **kwargs)
                    self.do_relayout()
    
    def refresh(self):
        """ Reimplemented parent class method which triggers a refresh
        of the layout children. The refresh occurs immediately and is 
        completed before the method returns. If the component is not 
        fully initialized, this is a no-op.

        """
        if not self.initialized:
            return

        # Protect against refresh recursion.
        if not guard.guarded(self, 'refresh'):
            with guard(self, 'refresh'):
                with self.freeze():
                    queue = self._refresh_queue
                    if queue:
                        while queue:
                            callback, args, kwargs = queue.popleft()
                            callback(*args, **kwargs)
                    self.do_refresh()

    def request_relayout(self):
        """ Reimplemented parent class method which triggers an update
        of the constraints and a layout refresh at some point in the 
        future. Mutliple calls to this method will be collapsed into
        a single effective relayout.

        """
        task = self._relayout_task
        if task is None or not task.pending():
            self._relayout_task = self.toolkit.app.schedule(self.relayout)

    def request_refresh(self):
        """ Reimplemented parent class method which triggers a refresh
        of the children at some point in the future. Mutliple calls to 
        this method will be collapsed into a single effective refresh.

        """
        task = self._refresh_task
        if task is None or not task.pending():
            self._refresh_task = self.toolkit.app.schedule(self.refresh)

    def request_relayout_task(self, callback, *args, **kwargs):
        """ Reimplemented parent class method which requests a relayout
        after adding the callback to an internal queue. The queue will
        be emptied from within a freeze context the next time a relayout
        occurs.

        """
        self._relayout_queue.append((callback, args, kwargs))
        self.request_relayout()
            
    def request_refresh_task(self, callback, *args, **kwargs):
        """ Reimplemented parent class method which requests a relayout
        after adding the callback to an internal queue. The queue will
        be emptied from within a freeze context the next time a relayout
        occurs.

        """
        self._refresh_queue.append((callback, args, kwargs))
        self.request_refresh()
    
    #--------------------------------------------------------------------------
    # Layout Implementation Handlers
    #--------------------------------------------------------------------------
    def do_relayout(self):
        """ A method that should be implemented by subclasses to actually
        perform the relayout. By default, this method does nothing.

        """
        pass
    
    def do_refresh(self):
        """ A method that should be implemented by subclasses to actually
        perform the refresh. By default, this method does nothing.

        """
        pass

