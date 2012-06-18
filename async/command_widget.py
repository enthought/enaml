#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import uuid

from traits.api import Instance

from base_component import BaseComponent


# The code style guideline for Enaml follows PEP-8, however there are a
# few extra rules in-place that PEP-8 doesn't specify:
#
# 1) Module level constructs should be separated by 2 blank lines.
# 2) Class level constructs should be separated by 1 blank line.
# 3) Docstrings start on the first line of the string, and have blank
#    line at the end. No exceptions.
# 4) Max line length for code is 79 characters.
# 5) Max line length for comments/docstrings is 72-74 characters.


class CommandWidget(BaseComponent):
    """ The base class of all widgets in Enaml.

    This extends BaseComponent with the concept of sending and receiving
    commands to and from a client widget.

    """
    uuid = Instance(uuid.UUID, factory=uuid.uuid4)

    def app(self):
        """ Returns the toolkit application for this widget.

        """
        # We need to decide how to reference the application instance.
        raise NotImplementedError

    def send(self, cmd, context):
        """ Send a command to another object to be executed
        
        Parameters
        ----------
        cmd : string
            The command to be executed
            
        context : dict
            The argument context for the command

        Returns
        -------
        result : AsyncReply
            An asynchronous reply object for the given command.

        """
        return self.app().send_command(self.uuid.hex, cmd, context)
        
    def receive(self, cmd, context):
        """ Handle a command sent by another object.
        
        Parameters
        ----------
        cmd : string
            The command to be executed
            
        context : dict
            The argument context for the command

        Returns
        -------
        result : object or NotImplemented
            The return value of the command handler or NotImplemented
            if this object does not define a handler for the command.

        """
        handler_name = 'receive_' + cmd
        handler = getattr(self, handler_name, None)
        if handler is not None:
            return handler(context)
        return NotImplemented

