#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Enum, Bool

from .constraints_widget import ConstraintsWidget


class Notebook(ConstraintsWidget):
    """ A component which displays a collection child Pages in a
    notebook style control.

    """
    #: The position of tabs in the notebook.
    tab_position = Enum('top', 'bottom', 'left', 'right')

    #: The style of the tabs to use in the notebook. This may not
    #: be supported on all platforms. The 'document' style is used
    #: when displaying many pages in an editing context such as in
    #: an IDE. The 'preferences' style is used to display tabs in
    #: a style that is appropriate for a preferences dialog, such
    #: as used in OSX.
    tab_style = Enum('document', 'preferences')

    #: Whether or not the tabs in the notebook should be closable
    #: through user interaction.
    tabs_closable = Bool(True)

    #: Whether or not the tabs in the notebook should be movable.
    #: through user interaction.
    tabs_movable = Bool(True)

    #: How strongly a component hugs it's contents' width. A TabGroup
    #: ignores its width hug by default, so it expands freely in width.
    hug_width = 'ignore'

    #: How strongly a component hugs it's contents' height. A TabGroup
    #: ignores its height hug by default, so it expands freely in height.
    hug_height = 'ignore'

    #--------------------------------------------------------------------------
    # Initialization
    #--------------------------------------------------------------------------
    def creation_attributes(self):
        """ Return the dict of creation attributes for the control.

        """
        super_attrs = super(Notebook, self).creation_attributes()
        attrs = {
            'tab_position': self.tab_position,
            'tab_style': self.tab_style,
            'tabs_closable': self.tabs_closable,
            'tabs_movable': self.tabs_movable,
        }
        super_attrs.update(attrs)
        return super_attrs

    def bind(self):
        """ Bind the change handlers for the control.

        """
        super(Notebook, self).bind()
        attrs = ('tab_position', 'tab_style', 'tabs_closable', 'tabs_movable')
        self.publish_attributes(*attrs)

