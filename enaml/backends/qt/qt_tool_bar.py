#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt.QtGui import QToolBar, QAction
from .qt_constraints_widget import QtConstraintsWidget

from ...components.tool_bar import AbstractTkToolBar


# XXX this class is not yet finished, but it is minimally working.
class QtToolBar(QtConstraintsWidget, AbstractTkToolBar):
    """ A Qt4 implementation of ToolBar.

    """
    #--------------------------------------------------------------------------
    # Setup Methods
    #--------------------------------------------------------------------------
    def create(self, parent):
        """ Creates the underlying QToolBar widget.

        """
        self.widget = QToolBar(parent)

    def initialize(self):
        """ Initializes the attributes of the toolbar.

        """
        super(QtToolBar, self).initialize()
        self.update_contents()

    #--------------------------------------------------------------------------
    # Change Handlers
    #--------------------------------------------------------------------------
    def shell_contents_changed(self, contents):
        """ The change handler for the 'contents' attribute of the shell
        object.

        """
        self.update_contents()

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def update_contents(self):
        """ Updates the contents of the toolbar with the components
        specified by the shell object.

        """
        # XXX Qt currently segfaults (on OSX at least) when using an
        # Include to populate the toolbar. This is due (my best guess)
        # to the fact that the QToolBar will take ownership of a widget
        # when inserting it into the toolbar. The best way around this
        # is to probably introduce a flag on a component that tells it
        # to ignore it's destroy command. This requires further testing.
        widget = self.widget
        widget.clear()
        for item in self.shell_obj.contents:
            child_widget = item.toolkit_widget
            if isinstance(child_widget, QAction):
                widget.addAction(child_widget)
            else:
                # When adding a widget to a toolbar qt returns a QAction
                # which must be used to toggle the visibility of the 
                # component. This closure binds the lifetime of the
                # action to that of the component.
                action = widget.addWidget(child_widget)
                def visClosure(obj, name, old, new):
                    action.setVisible(new)
                action.setVisible(item.visible)
                item.on_trait_change(visClosure, 'visible')

