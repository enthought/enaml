from traits.api import Str, Instance

from .control import Control, IControlImpl


class ILabelImpl(IControlImpl):
    
    def parent_text_changed(self, text):
        raise NotImplementedError

    
class Label(Control):
    """ A simple read-only text display.

    Attributes
    ----------
    text : Str
        The text in the label.

    """
    text = Str

    #---------------------------------------------------------------------------
    # Overridden parent class traits
    #---------------------------------------------------------------------------
    toolkit_impl = Instance(ILabelImpl)

