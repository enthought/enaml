#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import wx
from .wx_container import WXContainer
from ..group_box import AbstractTkGroupBox

#: Spacing constant between label and the border
SPACING = 1

class WXGroupBox(WXContainer, AbstractTkGroupBox):
    """ A wxPython implementation of GroupBox.

    The Enaml component is implemented using a combination of WX Static
    widgets.
    """
    #--------------------------------------------------------------------------
    # Setup methods
    #--------------------------------------------------------------------------

    def create(self):
        """ Creates the underlying WXGroupBox control.

        In addition to the wxWindow container widget the GroupBox
        creates:
            - a wxLabel
        """
        # FIXME: having all the private widgets created might save some
        # processing time but has an effect in memory.
        super(WXGroupBox, self).create()
        widget = self.widget
        self._border = wx.StaticBox(widget)
        self._label = wx.StaticText(widget)
        self._line = wx.StaticLine(widget)

    def initialize(self):
        """ Intializes the widget with the attributes of this instance.

        """
        super(WXGroupBox, self).initialize()
        shell = self.shell_obj
        self.set_title(shell.title)

    #--------------------------------------------------------------------------
    # Implementation
    #--------------------------------------------------------------------------
    def shell_title_changed(self, title):
        """ Update the title of the group box with the new value from the
        shell object.

        """
        self.set_title(title)

    def shell_flat_changed(self, flat):
        """ Update the flat flag of the group box with the new value from the
        shell object.

        """
        self.refresh_widget()

    def shell_title_align_changed(self, align):
        """ Update the title alignment to the new value from the shell object.

        """
        self.refresh_widget()

    def get_contents_margins(self):
        """ Return the (top, left, right, bottom) margin values for the widget.

        The margins are estimated based the height size of the internal label
        widget.

        """
        # FIXME: the border size is estimated embirically.
        shell = self.shell_obj
        label = self._label
        if label.GetLabel() == '':
            text_height = 2
        else:
            _, text_height = label.GetTextExtent('MyText')
        if shell.flat:
            left = right = bottom = text_height / 2
        else:
            left = right = bottom = 2 * text_height / 3
        return (text_height, left, right, bottom)

    def set_title(self, title):
        """ Set the title of the widget

        """
        self.refresh_border()
        self.refresh_title(title)

    def resize(self, width, height):
        """ Resize the GroupBox.

        The border and title widgets are updated to reflect the changes.

        """
        super(WXGroupBox, self).resize(width, height)
        self.refresh_widget()

    def set_geometry(self, x, y, width, height):
        """ Sets the geometry of the internal widget to the given
        x, y, width, and height values. The semantic meaning of the
        values is the same as for the 'resize' and 'move' methods.

        """
        super(WXGroupBox, self).set_geometry(x, y, width, height)
        self.refresh_widget()

    def refresh_border(self):
        """ Change the border style of the GroupBox border.

        """
        border = self._border
        line = self._line
        shell = self.shell_obj

        width, height = self.size()
        top, _, _, _ = self.get_contents_margins()
        flat = shell.flat

        if flat:
            y = top / 2
            border.Hide()
            line.SetDimensions(0, y, width, 1)
            line.Show()
            line.Refresh
        else:
            line.Hide()
            border.SetDimensions(0, 0, width, height)
            border.Show()
            border.Refresh()

    def refresh_title(self, title=None):
        """ Align the title in the GroupBox.

        """
        label = self._label
        shell = self.shell_obj

        if title is not None:
            label.SetLabel(title)

        width, _ = self.size()
        _, left, right, _ = self.get_contents_margins()
        text_x, _ = label.GetPositionTuple()

        size = label.GetBestSize()
        text_width, text_height = size.asTuple()
        flat = shell.flat
        align = shell.title_align

        if align == 'left':
            if flat:
                text_x = 0
            else:
                text_x = left
        elif align == 'right':
            if flat:
                text_x = width - text_width - SPACING * 2
            else:
                text_x = width - text_width - right - SPACING
        elif align == 'center':
            text_x = (width - text_width - SPACING) / 2

        position = wx.Point(text_x, 0)
        label.SetPosition(position)
        label.SetSizeWH(text_width + SPACING * 2, text_height)
        label.Refresh()

    def refresh_widget(self):
        """ Refersh the internal private widgets in order.

        """
        self.refresh_border()
        self.refresh_title()
