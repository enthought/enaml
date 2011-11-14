#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from pdb import set_trace
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
        super(WXGroupBox, self).create()
        widget = self.widget
        widget.SetDoubleBuffered(True)
        # TODO: create custom WXControl to encapsulate the GroupBox
        # behaviour
        self._label = wx.StaticText(widget)
        self._border = wx.StaticBox(widget)
        self._line = wx.StaticLine(widget)

    def initialize(self):
        """ Intializes the widget with the attributes of this instance.

        """
        super(WXGroupBox, self).initialize()
        shell = self.shell_obj
        self._set_title(shell.title)
        self._update_margins()
        self._align_title()
        self._toggle_borders(shell.flat)

    #--------------------------------------------------------------------------
    # Implementation
    #--------------------------------------------------------------------------
    def shell_title_changed(self, title):
        """ Update the title of the group box with the new value from the
        shell object.

        """
        self._set_title(title)
        self._update_margins()
        self._align_title()
        self._update_borders()
        self._refresh_widget()

    def shell_flat_changed(self, flat):
        """ Update the flat flag of the group box with the new value from
        the shell object.

        """
        self._update_margins()
        self._align_title()
        self._update_borders()
        self._toggle_borders(flat)
        self._refresh_widget()

    def shell_title_align_changed(self, align):
        """ Update the title alignment to the new value from the shell
        object.

        """
        self._align_title()
        self._refresh_widget()

    def get_contents_margins(self):
        """ Return the (top, left, right, bottom) margin values for the
        widget.

        """
        return self._margins

    def set_geometry(self, x, y, width, height):
        """ Set the WXGRoupBox geometry.

        Augment component set_geometry method to refresh the widget.

        """
        super(WXGroupBox, self).set_geometry(x, y, width, height)
        self._align_title()
        self._update_borders()
        self._refresh_widget()

    def resize(self, width, height):
        """ Resize the WXGroupBox.

        The border and title widgets are updated to reflect the changes.

        """
        super(WXGroupBox, self).resize(width, height)
        self._align_title()
        self._update_borders()
        self._refresh_widget()

    #--------------------------------------------------------------------------
    # Private methods
    #--------------------------------------------------------------------------

    def _set_title(self, title):
        """ Update the title of the GroupBox.

        """
        self._label.SetLabel(title)

    def _update_borders(self):
        """ Update the border dimensions.

        """
        y = self._margins[1]
        width, height = self.widget.GetSizeTuple()
        self._line.SetDimensions(0, y, width, 1)
        self._border.SetSizeWH(width, height)

    def _align_title(self):
        """ Align and draw the title in the GroupBox.

        Retrieve the label rectangle and position it in the parent region
        according to the `title_align` attribute.

        """
        shell = self.shell_obj
        label = self._label
        margins = self._margins

        flat = shell.flat
        align = shell.title_align
        text_width, _ = label.GetBestSize()
        width, _ = self.widget.GetSizeTuple()

        if align == 'left':
            x = 0 if flat else margins[1]
            label.Move((x, 0))
        elif align == 'right':
            right = width
            right -=  0 if flat else margins[2]
            x = right - text_width
            label.Move((x, 0))
        elif align == 'center':
            label.CenterOnParent(dir=wx.HORIZONTAL)

        label.Refresh()

    def _update_margins(self):
        """ Estimate and update the margins of the WXGroupBox.

        the margins are estimated empirically so that it looks
        similar to how the QtGroupBox widget behaves. The result is
        stored in the :attr:`_margins` attribute where the correspondace
        is [top, left, right, bottom].

        """
        height = self._label.GetCharHeight()
        margins = [height / 2] * 4
        margins[0] = 0.75 * height
        self._margins = margins

    def _toggle_borders(self, flat):
        """ Toggle between the flat and full border styles.

        """
        self._border.Show(not flat)
        self._line.Show(flat)

    def _refresh_widget(self):
        """ Refersh the internal private widgets in order.

        The border has to be refreshed before the title.

        """
        self._border.Refresh()
        self._line.Refresh()
