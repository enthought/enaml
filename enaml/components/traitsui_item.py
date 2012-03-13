#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from abc import abstractmethod

from traits.api import HasTraits, Instance
from traitsui.api import View, Handler

from .control import Control, AbstractTkControl


class AbstractTkTraitsUIItem(AbstractTkControl):
    
    @abstractmethod
    def shell_model_changed(self, model):
        raise NotImplementedError
    
    @abstractmethod
    def shell_view_changed(self, view):
        raise NotImplementedError
    
    @abstractmethod
    def shell_handler_changed(self, view):
        raise NotImplementedError


class TraitsUIItem(Control):
    """ A control which embeds a traits ui view.

    The TraitsUIItem allows a traits ui window to be embedded into an
    Enaml application. The ui that is embedded will be the same as that 
    which is created by calling model.edit_traits(...).

    """
    #: The model being displayed in the traits view.
    model = Instance(HasTraits)

    #: An optional specialized view to use for the model.
    view = Instance(View)

    #: The optional handler to use for the model and view.
    handler = Instance(Handler)

    #: Overridden parent class trait
    abstract_obj = Instance(AbstractTkTraitsUIItem)

