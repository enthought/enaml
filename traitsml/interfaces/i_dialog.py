from traits.api import Bool, Event, Enum, Str

from .i_element import IElement
from ..constants import DialogType, WindowRegion

class IDialog(IElement):
    """A base interface for all dialogs."""
    
    # Does this dialog capture focus?
    modal = Bool

    # The part of the dialog in which buttons are located.
    button_region = Enum(WindowRegion.DEFAULT, *WindowRegion.values())

    # Available button combinations for a dialog.
    buttons = Enum(DialogType.DEFAULT, *DialogType.values()) 

    # Main content to display in this dialog.
    message = Str

    # The event fired when a dialog is closed. 
    # Set this to the desired return value.
    closed = Event

