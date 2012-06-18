#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from base_component import BaseComponent

class CommandWidget(BaseComponent):
    """
    Extends BaseComponent to send and receive commands
    """
    def send_command(self, cmd_name, context):
        """
        Send a command to another object to be executed
        
        Parameters
        ----------
        cmd_name: string
            The command to be executed
            
        context: dict
            The arguments for the command
        """
        pass
        
    def receive_command(self, cmd_name, context):
        """
        Execute a command sent by another object
        
        Parameters
        ----------
        cmd_name: string
            The command to be executed

        context: dict
            The arguments for the command
        """
        cmd = getattr(self, cmd_name)
        cmd(**context)
