from traits.api import Str

from .control import Control, IControlImpl


class ILabelImpl(IControlImpl):

    def parent_text_changed(self):
        raise NotImplementedError

    
class Label(Control):
    """ A simple read-only text display.

    Attributes
    ----------
    text : Str
        The text in the label.

    """
    text = Str

