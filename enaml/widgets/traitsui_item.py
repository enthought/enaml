from traits.api import HasTraits, Instance
from traitsui.api import View, Handler
from traitsui.ui import UI

from .control import IControlImpl, Control


class ITraitsUIItemImpl(IControlImpl):
    
    def parent_model_changed(self, model):
        raise NotImplementedError
    
    def parent_view_changed(self, view):
        raise NotImplementedError
    
    def parent_handler_changed(self, view):
        raise NotImplementedError


class TraitsUIItem(Control):

    model = Instance(HasTraits)

    view = Instance(View)

    handler = Instance(Handler)

    #---------------------------------------------------------------------------
    # Overridden parent class traits
    #---------------------------------------------------------------------------
    toolkit_impl = Instance(ITraitsUIItemImpl)

