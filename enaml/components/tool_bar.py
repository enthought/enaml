#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from abc import abstractmethod

from traits.api import Instance, Property, List, Either, cached_property

from .action import Action
from .constraints_widget import ConstraintsWidget, AbstractTkConstraintsWidget


class AbstractTkToolBar(AbstractTkConstraintsWidget):
    """ The abstract toolkit interface for a ToolBar.

    """
    @abstractmethod
    def shell_contents_changed(self, contents):
        """ The change handler for the 'contents' attribute on the
        shell object.

        """
        raise NotImplementedError


class ToolBar(ConstraintsWidget):
    """ A tool bar can be used to hold and display actions.

    """
    #: ToolBars expand freely in width by default
    hug_width = 'ignore'

    #: A read-only cached property which holds the list of toolbar 
    #: children which are actions or widgets.
    contents = Property(
        List(Either(Instance(Action), Instance(ConstraintsWidget))), 
        depends_on='children',
    )
    
    #: Overridden parent class trait
    abstract_obj = Instance(AbstractTkToolBar)

    @cached_property
    def _get_contents(self):
        """ The property getter for the 'contents' attribute.

        """
        filt = lambda child: isinstance(child, (Action, ConstraintsWidget))
        return filter(filt, self.children)

