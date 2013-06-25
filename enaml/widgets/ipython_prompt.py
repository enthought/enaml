#------------------------------------------------------------------------------
#  Copyright (c) 2013, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Dict
from .constraints_widget import ConstraintsWidget


class IPythonPrompt(ConstraintsWidget):
    """ An interactive python prompt

    """
    #: The context for the prompt to operate in
    context = Dict

    #--------------------------------------------------------------------------
    # Initialization
    #--------------------------------------------------------------------------
    def snapshot(self):
        snap = super(IPythonPrompt, self).snapshot()
        snap['context'] = self.context
        return snap

    def bind(self):
        """ Bind the change handlers for a widget component.

        """
        super(IPythonPrompt, self).bind()
        attrs = (
            'context',
        )
        self.publish_attributes(*attrs)

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def pull(self, identifier):
        """ Attempt to pull an identifier from the IPython context

        """
        self.send_action('pull', {'identifier': identifier})

    #--------------------------------------------------------------------------
    # Message handlers
    #--------------------------------------------------------------------------
    def on_action_update_context(self, content):
        """ Handle the 'update_context' action from the Enaml widget.

        """
        self.context.update(content['context'])
