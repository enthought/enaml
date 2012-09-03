#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import wx

from .wx_single_widget_sizer import wxSingleWidgetSizer
from .wx_widget_component import WxWidgetComponent


class WxWindow(WxWidgetComponent):
    """ A Wx implementation of an Enaml Window.

    """
    #: The storage for the central widget id
    _central_widget_id = None

    #--------------------------------------------------------------------------
    # Setup Methods
    #--------------------------------------------------------------------------
    def create_widget(self, parent, tree):
        """ Create the underlying wx.Frame widget.

        """
        return wx.Frame(parent)

    def create(self, tree):
        """ Create and initialize the window control.

        """
        super(WxWindow, self).create(tree)
        self.set_central_widget_id(tree['central_widget_id'])
        self.set_title(tree['title'])
        self.set_initial_size(tree['initial_size'])
        self.set_modality(tree['modality'])
        self.widget().Bind(wx.EVT_CLOSE, self.on_close)

    def init_layout(self):
        """ Perform the layout initialization for the window control.

        """
        # A Window is a top-level component and `init_layout` is called 
        # bottom-up, so the layout for all of the children has already
        # taken place. This is the proper time to grab the central 
        # widget child, stick it the sizer, and fit the window.
        child = self.find_child(self._central_widget_id)
        if child is not None:
            sizer = wxSingleWidgetSizer()
            sizer.Add(child.widget())
            widget = self.widget()
            widget.SetSizerAndFit(sizer)
            max_size = widget.ClientToWindowSize(sizer.CalcMax())
            widget.SetMaxSize(max_size)

    #--------------------------------------------------------------------------
    # Event Handlers
    #--------------------------------------------------------------------------
    def on_close(self, event):
        """ The event handler for the EVT_CLOSE event.

        """
        event.Skip()
        # Make sure the frame is not modal when closing, or no other 
        # windows will be unblocked.
        self.widget().MakeModal(False)
        self.send_action('closed', {})

    #--------------------------------------------------------------------------
    # Message Handlers
    #--------------------------------------------------------------------------
    def on_action_close(self, content):
        """ Handle the 'close' action from the Enaml widget. 

        """
        self.close()

    def on_action_maximize(self, content):
        """ Handle the 'maximize' action from the Enaml widget. 

        """
        self.maximize()

    def on_action_minimize(self, content):
        """ Handle the 'minimize' action from the Enaml widget. 

        """
        self.minimize()

    def on_action_restore(self, content):
        """ Handle the 'restore' action from the Enaml widget. 

        """
        self.restore()

    def on_action_set_icon(self, content):
        """ Handle the 'set-icon' action from the Enaml widget. 

        """
        pass

    def on_action_set_title(self, content):
        """ Handle the 'set-title' action from the Enaml widget. 

        """
        self.set_title(content['title'])
    
    def on_action_set_modality(self, content):
        """ Handle the 'set-modality' action from the Enaml widget.

        """
        self.set_modality(content['modality'])

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def close(self):
        """ Close the window

        """
        self.widget().Close()

    def maximize(self):
        """ Maximize the window.

        """
        self.widget().Maximize(True)

    def minimize(self):
        """ Minimize the window.

        """
        self.widget().Iconize(True)

    def restore(self):
        """ Restore the window after a minimize or maximize.

        """
        self.widget().Maximize(False)

    def set_icon(self, icon):
        """ Set the window icon.

        """
        pass

    def set_central_widget_id(self, widget_id):
        """ Set the central widget id for the window.

        """
        self._central_widget_id = widget_id

    def set_title(self, title):
        """ Set the title of the window.

        """
        self.widget().SetTitle(title)

    def set_initial_size(self, size):
        """ Set the initial size of the window.

        """
        self.widget().SetSize(wx.Size(*size))

    def set_modality(self, modality):
        """ Set the modality of the window.

        """
        if modality == 'non_modal':
            self.widget().MakeModal(False)
        else:
            self.widget().MakeModal(True)

    def set_visible(self, visible):
        """ Set the visibility on the window.

        This is an overridden parent class method to set the visibility
        at a later time, so that layout can be initialized before the
        window is displayed.

        """
        # XXX this could be done better.
        wx.CallAfter(super(WxWindow, self).set_visible, visible)

