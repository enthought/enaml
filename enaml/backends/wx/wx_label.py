#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import wx

from .wx_control import WXControl

from ...components.label import AbstractTkLabel


class WXLabel(WXControl, AbstractTkLabel):
    """ A wxPython implementation of Label.

    """
    #: The internal cached size hint which is used to determine whether
    #: of not a size hint updated event should be emitted when the text
    #: in the label changes
    _cached_size_hint = None

    #--------------------------------------------------------------------------
    # Setup methods
    #--------------------------------------------------------------------------
    def create(self, parent):
        """ Creates the underlying wx.StaticText control.

        """
        self.widget = wx.StaticText(parent)

    def initialize(self):
        """ Initializes the attributes on the underlying control.

        """
        super(WXLabel, self).initialize()
        self.set_text(self.shell_obj.text)

    #--------------------------------------------------------------------------
    # Implementation
    #--------------------------------------------------------------------------
    def shell_text_changed(self, text):
        """ The change handler for the 'text' attribute on the shell 
        component.

        """
        self.set_text(text)

    def shell_word_wrap_changed(self, wrap):
        """ The change handler for the 'word_wrap' attribute on the 
        shell component. Wx does not support word wrap, so this is 
        a no-op.

        """
        pass

    def set_text(self, text):
        """ Sets the text on the underlying control.

        """
        self.widget.SetLabel(text)

        # Emit a size hint updated event if the size hint has actually
        # changed. This is an optimization so that a constraints update
        # only occurs when the size hint has actually changed. This 
        # logic must be implemented here so that the label has been
        # updated before the new size hint is computed. Placing this
        # logic on the shell object would not guarantee that the label
        # has been updated at the time the change handler is called.
        cached = self._cached_size_hint
        hint = self._cached_size_hint = self.size_hint()
        if cached != hint:
            self.shell_obj.size_hint_updated()
    
