#------------------------------------------------------------------------------
#  Copyright (c) 2013, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from IPython.frontend.qt.console.ipython_widget import IPythonWidget
from IPython.frontend.qt.inprocess import QtInProcessKernelManager
from .qt_constraints_widget import QtConstraintsWidget


class QtIPythonPrompt(QtConstraintsWidget):
    """ Qt4 implementation of an IPython prompt

    """
    _kernel_manager = None

    def create_widget(self, parent, tree):
        """ Creates the underlying QWidget object.

        """
        self._kernel_manager = QtInProcessKernelManager()
        self._kernel_manager.start_kernel()

        client = self._kernel_manager.client()
        client.start_channels()

        widget = IPythonWidget(parent=parent)
        widget.kernel_manager = self._kernel_manager
        widget.kernel_client = client

        return widget

    def create(self, tree):
        """ Create and initialize the underlying widget.

        """
        super(QtIPythonPrompt, self).create(tree)
        self.set_context(tree['context'])

    #--------------------------------------------------------------------------
    # Message Handlers
    #--------------------------------------------------------------------------
    def on_action_set_context(self, content):
        """ Handle the 'set_context' action from the Enaml widget.

        """
        self.set_context(content['context'])

    def on_action_pull(self, content):
        """ Handle the 'pull' action from the Enaml widget.

        """
        namespace = self._kernel_manager.kernel.shell.user_ns
        name = content['identifier']
        body = {name: namespace.get(name, None)}
        self.send_action('update_context', {'context': body})

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_context(self, context):
        """ Sets the context for the kernel

        """
        self._kernel_manager.kernel.shell.push(context)
