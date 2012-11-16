#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Bool, Enum, List, Property, Either, cached_property

from .action import Action
from .action_group import ActionGroup
from .constraints_widget import ConstraintsWidget, PolicyEnum


class ToolBar(ConstraintsWidget):
    """ A widget which displays a row of tool buttons.

    A ToolBar is typically used as a child of a MainWindow where it can
    be dragged and docked in various locations in the same fashion as a
    DockPane. However, a ToolBar can also be used as the child of a
    Container and layed out with constraints, though in this case it will
    lose its ability to be docked.

    """
    #: Whether or not the tool bar is movable by the user. This value
    #: only has meaning if the tool bar is the child of a MainWindow.
    movable = Bool(True)

    #: Whether or not the tool bar can be floated as a separate window.
    #: This value only has meaning if the tool bar is the child of a
    #: MainWindow.
    floatable = Bool(True)

    #: A boolean indicating whether or not the tool bar is floating.
    #: This value only has meaning if the tool bar is the child of a
    #: MainWindow.
    floating = Bool(False)

    #: The dock area in the MainWindow where the tool bar is docked.
    #: This value only has meaning if the tool bar is the child of a
    #: MainWindow.
    dock_area = Enum('top', ('left', 'right', 'top', 'bottom'))

    #: The areas in the MainWindow where the tool bar can be docked
    #: by the user. This value only has meaning if the tool bar is the
    #: child of a MainWindow.
    allowed_dock_areas = List(
        Enum('left', 'right', 'top', 'bottom', 'all'), value=['all'],
    )

    #: The orientation of the toolbar. This only has meaning when the
    #: toolbar is not a child of a MainWindow and is used as part of
    #: a constraints based layout.
    orientation = Enum('horizontal', 'vertical')

    #: A read only property which returns the tool bar's items:
    #: ActionGroup | Action
    items = Property(depends_on='children')

    #: Hug width is redefined as a property to be computed based on the
    #: orientation of the tool bar unless overridden by the user.
    hug_width = Property(PolicyEnum, depends_on=['_hug_width', 'orientation'])

    #: Hug height is redefined as a property to be computed based on the
    #: orientation of the slider unless overridden by the user.
    hug_height = Property(PolicyEnum, depends_on=['_hug_height', 'orientation'])

    #: An internal override trait for hug_width
    _hug_width = Either(None, PolicyEnum, default=None)

    #: An internal override trait for hug_height
    _hug_height = Either(None, PolicyEnum, default=None)

    #--------------------------------------------------------------------------
    # Initialization
    #--------------------------------------------------------------------------
    def snapshot(self):
        """ Returns the snapshot dict for the DockPane.

        """
        snap = super(ToolBar, self).snapshot()
        snap['movable'] = self.movable
        snap['floatable'] = self.floatable
        snap['floating'] = self.floating
        snap['dock_area'] = self.dock_area
        snap['allowed_dock_areas'] = self.allowed_dock_areas
        snap['orientation'] = self.orientation
        return snap

    def bind(self):
        """ Bind the change handlers for the ToolBar.

        """
        super(ToolBar, self).bind()
        attrs = (
            'movable', 'floatable', 'floating', 'dock_area',
            'allowed_dock_areas', 'orientation',
        )
        self.publish_attributes(*attrs)

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    @cached_property
    def _get_items(self):
        """ The getter for the 'items' property.

        Returns
        -------
        result : tuple
            The tuple of items for the ToolBar.

        """
        isinst = isinstance
        types = (Action, ActionGroup)
        items = (child for child in self.children if isinst(child, types))
        return tuple(items)

    #--------------------------------------------------------------------------
    # Property Methods
    #--------------------------------------------------------------------------
    def _get_hug_width(self):
        """ The property getter for 'hug_width'.

        Returns a computed hug value unless overridden by the user.

        """
        res = self._hug_width
        if res is None:
            if self.orientation == 'horizontal':
                res = 'ignore'
            else:
                res = 'strong'
        return res

    def _get_hug_height(self):
        """ The proper getter for 'hug_height'.

        Returns a computed hug value unless overridden by the user.

        """
        res = self._hug_height
        if res is None:
            if self.orientation == 'vertical':
                res = 'ignore'
            else:
                res = 'strong'
        return res

    def _set_hug_width(self, value):
        """ The property setter for 'hug_width'.

        Overrides the computed value.

        """
        self._hug_width = value

    def _set_hug_height(self, value):
        """ The property setter for 'hug_height'.

        Overrides the computed value.

        """
        self._hug_height = value

    #--------------------------------------------------------------------------
    # Message Handling
    #--------------------------------------------------------------------------
    def on_action_floated(self, content):
        """ Handle the 'floated' action from the client widget.

        """
        self.set_guarded(floating=True)

    def on_action_docked(self, content):
        """ Handle the 'docked' action from the client widget.

        """
        self.set_guarded(floating=False)
        self.set_guarded(dock_area=content['dock_area'])

