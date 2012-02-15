#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from abc import abstractmethod

from traits.api import Str, Instance

from .control import Control, AbstractTkControl


class AbstractTkHtml(AbstractTkControl):
    """ The abstract toolkit Html interface.

    """
    @abstractmethod
    def shell_source_changed(self, source):
        """ The change handler for the 'source' attribute of the shell
        object.

        """
        raise NotImplementedError


class Html(Control):
    """ An extremely simple widget for displaying HTML.
    
    """
    #: The Html source code to be rendered.
    source = Str
    
    #: How strongly a component hugs it's contents' width. Html widgets 
    # ignore the width hug by default, so they expand freely in width.
    hug_width = 'ignore'
    
    #: How strongly a component hugs it's contents' height. Html widgets
    #: ignore the height hug by default, so they expand freely in height.
    hug_height = 'ignore'

    #: Overridden parent class trait
    abstract_obj = Instance(AbstractTkHtml)

