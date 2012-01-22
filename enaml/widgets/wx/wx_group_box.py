#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import wx

from .wx_container import WXContainer

from ..group_box import AbstractTkGroupBox


WX_ALIGNMENTS = dict(
    left=wx.ALIGN_LEFT,
    center=wx.ALIGN_CENTER,
    right=wx.ALIGN_RIGHT,
)


class wxGroupBox(wx.Panel):
    """ A wx.Panel sublcass that implements basic GroupBox functionality.

    """
    def __init__(self, parent, id=-1, title='', align=wx.ALIGN_LEFT, flat=False):
        super(wxGroupBox, self).__init__(parent, id)

        # Create the sibling widgets that are necessary to mimic 
        # a proper group box
        self._label = wx.StaticText(self, -1, title)
        self._border = wx.StaticBox(self)
        self._line = wx.StaticLine(self)

        # Set ourself to double buffered or suffer terrible 
        # rendering artifacts
        self.SetDoubleBuffered(True)
        
        self._title_alignment = align
        self._flat = flat

        # Compute and store the label size so we don't have to measure 
        # strings on each resize event.
        self._label_size = self._label.GetBestSize()

        # Compute the initial margins
        self._margins = None
        self._update_margins()

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def GetAlignment(self):
        """ Return the wx alignment flag for the current alignment 
        of the group box title.

        """
        return self._title_alignment

    def SetAlignment(self, alignment):
        """ Set the alignment of the title of the group box. Should
        be one of wx.ALIGN_LEFT, wx.ALIGN_RIGHT, wx.ALIGN_CENTER.

        """
        self._title_alignment = alignment
        self._update_layout()
        
    def GetFlat(self):
        """ Returns a boolean indicating whether the group box is using
        a flat style.

        """
        return self._flat

    def SetFlat(self, flat):
        """ Set whether or not the group box should be displayed using
        a flat style.

        """
        self._flat = flat
        if flat:
            self._border.Show(False)
            self._line.Show(True)
        else:
            self._border.Show(True)
            self._line.Show(False)
        self._update_layout()

    def GetTitle(self):
        """ Return the current title text in the group box.
        
        """
        return self._label.GetLabel()

    def SetTitle(self, title):
        """ Set the current title text in the group box.

        """
        self._title = title
        self._label.SetLabel(title)
        self._label_size = self._label.GetBestSize()
        if not title:
            self._label.Show(False)
        else:
            self._label.Show(True)
        # The margins only depend on the label, so recompute them now.
        self._update_margins()
        self._update_layout()
    
    def GetContentsMarginsTuple(self):
        """ Return a tuple of (top, left, right, bottom) margin values
        of the group box.

        """
        return self._margins

    def SetDimensions(self, x, y, width, height):
        """ Overridden parent class method to synchronize the group
        box decorations.

        """
        super(wxGroupBox, self).SetDimensions(x, y, width, height)
        self._update_layout()

    def SetSize(self, size):
        """ Overridden parent class method to synchronize the group
        box decorations.

        """
        super(wxGroupBox, self).SetSize(size)
        self._update_layout()

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _update_layout(self):
        """ Synchronizes the drawing of the group box decorations with 
        the panel.

        """
        if self._flat:
            self._update_line_geometry()
        else:
            self._update_border_geometry()
        self._update_title_geometry()
        self.Refresh()

    def _update_border_geometry(self):
        """ Updates the geometry of the border.

        """
        width, height = self.GetSizeTuple()
        self._border.SetSizeWH(width, height)
    
    def _update_line_geometry(self):
        """ Updates the geometry of the line.

        """
        y = self._margins[0] / 2
        width, _ = self.GetSizeTuple()
        self._line.SetDimensions(0, y, width, 1)

    def _update_title_geometry(self):
        """ Updates the geometry of the title.

        """
        label = self._label
        flat = self._flat
        align = self._title_alignment

        text_width, _ = self._label_size
        width, _ = self.GetSizeTuple()

        # These offsets are determined empirically to look similar
        # in form to Qt on Windows
        if align == wx.ALIGN_LEFT:
            x = 0 if flat else 8
            label.Move((x, 0))
        elif align == wx.ALIGN_RIGHT:
            right = width
            right -= 0 if flat else 8
            x = right - text_width
            label.Move((x, 0))
        elif align == wx.ALIGN_CENTER:
            label.CenterOnParent(dir=wx.HORIZONTAL)
        else:
            raise ValueError('Invalid title alignment %s' % align)

    def _update_margins(self):
        """ Computes the margins empirically so that they look similar 
        in form to Qt on Windows.

        """
        margins = [1, 1, 1, 1]
        if self._label.GetLabel():
            height = self._label.GetCharHeight()
            margins[0] = height
        self._margins = tuple(margins)

    
class WXGroupBox(WXContainer, AbstractTkGroupBox):
    """ A wxPython implementation of GroupBox.

    """
    #--------------------------------------------------------------------------
    # Setup methods
    #--------------------------------------------------------------------------
    def create(self, parent):
        """ Creates the underlying custom wxGroupBox control.

        """
        self.widget = wxGroupBox(parent)

    def initialize(self):
        """ Intializes the widget with the attributes of this instance.

        """
        super(WXGroupBox, self).initialize()
        shell = self.shell_obj
        self.set_title(shell.title)
        self.set_flat(shell.flat)
        self.set_title_align(shell.title_align)

    #--------------------------------------------------------------------------
    # Implementation
    #--------------------------------------------------------------------------
    def shell_title_changed(self, title):
        """ Update the title of the group box with the new value from the
        shell object.

        """
        self.shell_obj.request_relayout_task(self.set_title, title)

    def shell_flat_changed(self, flat):
        """ Update the flat flag of the group box with the new value from
        the shell object.

        """
        self.shell_obj.request_relayout_task(self.set_flat, flat)

    def shell_title_align_changed(self, align):
        """ Update the title alignment to the new value from the shell
        object.

        """
        self.set_title_align(align)

    def get_contents_margins(self):
        """ Return the (top, left, right, bottom) margin values for the
        widget.

        """
        return self.widget.GetContentsMarginsTuple()

    #--------------------------------------------------------------------------
    # Widget Update methods
    #--------------------------------------------------------------------------
    def set_title(self, title):
        """ Update the title of the group box.

        """
        self.widget.SetTitle(title)

    def set_flat(self, flat):
        """ Updates the flattened appearance of the group box.

        """
        self.widget.SetFlat(flat)
    
    def set_title_align(self, align):
        """ Updates the alignment of the title of the group box.

        """
        wx_align = WX_ALIGNMENTS[align]
        self.widget.SetAlignment(wx_align)

