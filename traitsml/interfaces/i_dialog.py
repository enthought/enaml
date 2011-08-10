from traits.api import Bool, List, Event

from .i_element import IElement


class IDialog(IElement):
    """A base interface for all dialogs."""
    
    # Does this dialog capture focus?
    modal = Bool

    # Available buttons for this dialog.
    buttons = List # XXX List of what? PushButtons, Strings, etc.

    # The event fired when a dialog is closed. 
    # Set this to the desired return value.
    closed = Event

