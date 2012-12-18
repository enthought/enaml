#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
class EventHandler(object):
    """ A class defining the event handler interface for a TextEditor.

    This class serves as a base class for concrete event handlers. For
    performance reasons, all event handlers are passed toolkit specific
    event objects. The default implementations of all handler methods
    return False.

    """
    def mouse_pressed(self, editor, event):
        """ Called by the editor when the user presses a mouse button.

        Parameters
        ----------
        editor : object
            The toolkit specific editor object.

        event : object
            The toolkit specific mouse event object.

        Returns
        -------
        result : bool
            True if the event has been handled, False otherwise.

        """
        return False

    def mouse_moved(self, editor, event):
        """ Called by the editor when the user moves the mouse.

        This will only be called while a mouse button is held down.

        Parameters
        ----------
        editor : object
            The toolkit specific editor object.

        event : object
            The toolkit specific mouse event object.

        Returns
        -------
        result : bool
            True if the event has been handled, False otherwise.

        """
        return False

    def mouse_released(self, editor, event):
        """ Called by the editor when the user releases a mouse button.

        Parameters
        ----------
        editor : object
            The toolkit specific editor object.

        event : object
            The toolkit specific mouse event object.

        Returns
        -------
        result : bool
            True if the event has been handled, False otherwise.

        """
        return False

    def key_pressed(self, editor, event):
        """ Called by the editor when the user presses a key.

        Parameters
        ----------
        editor : object
            The toolkit specific editor object.

        event : object
            The toolkit specific key event object.

        Returns
        -------
        result : bool
            True if the event has been handled, False otherwise.

        """
        return False

    def key_released(self, editor, event):
        """ Called by the editor when the user releases a key.

        Parameters
        ----------
        editor : object
            The toolkit specific editor object.

        event : object
            The toolkit specific key event object.

        Returns
        -------
        result : bool
            True if the event has been handled, False otherwise.
            True if the cursor has handled the event, False otherwise.

        """
        return False

