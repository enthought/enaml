#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Range, Enum, Either, Property

from .constraints_widget import PolicyEnum
from .control import Control


class Separator(Control):
    """ A widget which draws a horizontal or vertical separator line.

    """
    #: The orientation of the separator line.
    orientation = Enum('horizontal', 'vertical')

    #: The line style for the separator.
    line_style = Enum('sunken', 'raised', 'plain')

    #: The thickness of the outer separator line.
    line_width = Range(low=0, high=3, value=1)

    #: The thickness of the inner separator line. This only has an
    #: effect for the 'sunken' and 'raised' line styles.
    midline_width = Range(low=0, high=3, value=0)

    #: Hug width is redefined as a property to be computed based on the
    #: orientation of the separator unless overridden by the user.
    hug_width = Property(PolicyEnum, depends_on=['_hug_width', 'orientation'])

    #: Hug height is redefined as a property to be computed based on the
    #: orientation of the separator unless overridden by the user.
    hug_height = Property(PolicyEnum, depends_on=['_hug_height', 'orientation'])

    #: An internal override trait for hug_width
    _hug_width = Either(None, PolicyEnum, default=None)

    #: An internal override trait for hug_height
    _hug_height = Either(None, PolicyEnum, default=None)

    #--------------------------------------------------------------------------
    # Initialization
    #--------------------------------------------------------------------------
    def snapshot(self):
        """ Returns the snapshot dictionary for the Separator.

        """
        snap = super(Separator, self).snapshot()
        snap['orientation'] = self.orientation
        snap['line_style'] = self.line_style
        snap['line_width'] = self.line_width
        snap['midline_width'] = self.midline_width
        return snap

    def bind(self):
        """ Binds the change handlers for the Separator.

        """
        super(Separator, self).bind()
        attrs = ('orientation', 'line_style', 'line_width', 'midline_width')
        self.publish_attributes(*attrs)

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

