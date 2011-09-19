#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import HasTraits, Instance
from traitsui.api import View, Handler

from .control import IControlImpl, Control


class ITraitsUIItemImpl(IControlImpl):
    
    def parent_model_changed(self, model):
        raise NotImplementedError
    
    def parent_view_changed(self, view):
        raise NotImplementedError
    
    def parent_handler_changed(self, view):
        raise NotImplementedError


class TraitsUIItem(Control):
    """ A control which embeds a traits ui view.

    The TraitsUIItem allows one to embed a traits ui window into an
    Enaml application. The ui that is embedded will be the same as
    that which is created by calling model.edit_traits(...).

    Attributes
    ----------
    model : Instance(HasTraits), required
        The model being displayed in the traits view.

    view : Instance(View), optional
        An optional specialized view to use for the model.
    
    handler : Instance(Handler), optional
        The optional handler to use for the model and view.

    """
    model = Instance(HasTraits)

    view = Instance(View)

    handler = Instance(Handler)

    #---------------------------------------------------------------------------
    # Overridden parent class traits
    #---------------------------------------------------------------------------
    toolkit_impl = Instance(ITraitsUIItemImpl)

