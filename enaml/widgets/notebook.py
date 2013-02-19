#------------------------------------------------------------------------------
#  Copyright (c) 2013, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from atom.api import Enum, Bool, observe, set_default

from enaml.core.declarative import d_properties

from .constraints_widget import ConstraintsWidget
from .page import Page


@d_properties('tab_style', 'tab_position', 'tabs_closable', 'tabs_movable')
class Notebook(ConstraintsWidget):
    """ A component which displays its children as tabbed pages.

    """
    #: The style of tabs to use in the notebook. Preferences style
    #: tabs are appropriate for configuration dialogs and the like.
    #: Document style tabs are appropriate for multi-page editing
    #: in code editors and the like.
    tab_style = Enum('document', 'preferences')

    #: The position of tabs in the notebook.
    tab_position = Enum('top', 'bottom', 'left', 'right')

    #: Whether or not the tabs in the notebook should be closable.
    tabs_closable = Bool(True)

    #: Whether or not the tabs in the notebook should be movable.
    tabs_movable = Bool(True)

    #: A notebook expands freely in height and width by default.
    hug_width = set_default('ignore')
    hug_height = set_default('ignore')

    @property
    def pages(self):
        """ A read-only property which returns the notebook pages.

        """
        isinst = isinstance
        pages = (child for child in self.children if isinst(child, Page))
        return tuple(pages)

    #--------------------------------------------------------------------------
    # Messenger API
    #--------------------------------------------------------------------------
    def snapshot(self):
        """ Returns the snapshot for the control.

        """
        snap = super(Notebook, self).snapshot()
        snap['tab_style'] = self.tab_style
        snap['tab_position'] = self.tab_position
        snap['tabs_closable'] = self.tabs_closable
        snap['tabs_movable'] = self.tabs_movable
        return snap

    @observe(r'^(tab_style|tab_position|tabs_closable|tabs_movable)$', regex=True)
    def send_member_change(self):
        """ Send the state change for the members.

        """
        # The superclass implementation is sufficient.
        super(Notebook, self).send_member_change()

