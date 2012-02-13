#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import weakref

import wx
import wx.lib.newevent

from .wx_component import WXComponent

from ..action import AbstractTkAction


#: A custom event emitted by the wxEnamlAction when it has been triggered
wxEnamlActionTriggered, EVT_ACTION_TRIGGERED = wx.lib.newevent.NewEvent()

#: A custom event emitted by the wxEnamlAction when it has been toggled
wxEnamlActionToggled, EVT_ACTION_TOGGLED = wx.lib.newevent.NewEvent()


class wxEnamlAction(wx.EvtHandler):
    """ An wx.EvtHandler which *acts* like a wx equivalent to a QAction.
    It works by managing an internal wxMenuItem. Menus which use 
    this action must call the Install() method in order for the
    underlying wx.MenuItem to be created. This is due to the fact 
    that using the wx.MenuItem constructor from Python will lead 
    to segfaults when calling menu.AppendItem(item), hence creating
    a usable subclass of wx.MenuItem is out of the question.

    """
    def __init__(self, parent):
        """ Initialize a wxAction.

        Parameters
        ----------
        parent : wxEnamlMenu
            The wxEnamlMenu instance which is the parent of this action.

        """
        super(wxEnamlAction, self).__init__()

        # The parent wx.Menu of this action
        self._parent = weakref.ref(parent)

        # The internal wx.MenuItem that this action will manage
        self._menu_item = None

        # The text of the action
        self._text = str(id(self))

        # Whether or not the action is a separator
        self._separator = False

        # Whether or not the action is enabled
        self._enabled = True

        # Whether or not the action is checkable
        self._checkable = False
        
        # Whether or not the action is checked
        self._checked = False

        # The help text for the action
        self._help_text = ''

        # Find the parent on which we need to bind the event handler. 
        # If this action is contained in a MenuBar, this will be a
        # wx.Frame, otherwise it will be a wx.Menu used as a sole 
        # popup menu.
        while parent is not None:
            last = parent
            parent = parent.GetParent()
        last.Bind(wx.EVT_MENU, self.OnMenuEvent)

        # Store away a weak reference to the object on which we
        # bound the event handler, so we can unbind it in the 
        # Destroy method.
        self._binder = weakref.ref(last)

    def OnMenuEvent(self, event):
        """ The event handler for menu events on this action.

        """
        menu_item = self._menu_item
        if menu_item is not None and menu_item.GetId() == event.GetId():
            # If the action is checkable, we first need to emit
            # the toggled event. This behavior is the same as Qt.
            if self._checkable:
                self._checked = menu_item.IsChecked()
                evt = wxEnamlActionToggled()
                wx.PostEvent(self, evt)
            
            # Next, we emit the standard triggered Event.
            evt = wxEnamlActionTriggered()
            wx.PostEvent(self, evt)
        else:
            # Only skip the event if it's not handled by this action.
            # Otherwise, we'll get multiple notifications.
            event.Skip()

    def GetParent(self):
        """ Returns the parent of the action or None if the parent has
        already been garbage collected.

        """
        return self._parent()

    def GetMenuItem(self):
        """ Returns the internal wx.MenuItem being managed by the action.

        """
        return self._menu_item
    
    def Install(self, idx=None):
        """ Adds this action to the internal parent wx.Menu object at 
        the given index. If the index is None, the item is appended to
        the end of the menu.

        """
        menu = self._parent()
        if menu is not None:
            # When creating a new menu item, we need to create a new
            # id for that item, as well as a valid name for the item.
            # If we don't give it a valid name (an empty string is 
            # invalid), then it will segfault. We create the item with 
            # a temporary name, and update it after the item has been 
            # created. We also fully update the rest of item state after 
            # it has been created.
            menu_id = wx.NewId()
            temp_name = str(menu_id)

            if idx is None:
                idx = menu.GetMenuItemCount()
            
            if self._separator:
                self._menu_item = menu.InsertSeparator(idx)
            elif self._checkable:
                self._menu_item = menu.InsertCheckItem(idx, menu_id, temp_name)
            else:
                self._menu_item = menu.Insert(idx, menu_id, temp_name)

            # Update the state of the menu item after it's been created.
            self.Enable(self._enabled)
            self.SetText(self._text)
            self.SetChecked(self._checked)
            self.SetHelp(self._help_text)

    def GetText(self, text):
        """ Returns the current text for the action.

        """
        return self._text

    def SetText(self, text):
        """ Sets the text for the action. If the given text is the 
        empty string, then a unique mangled name will be generated
        for the action.

        """
        item = self._menu_item
        if item is not None:
            if not text:
                text = 'Action_' + str(item.GetId())
            item.SetText(text)
        else:
            if not text:
                text = 'Action_' + str(id(self))
        self._text = text
    
    def GetHelp(self):
        """ Returns the help text for the action.

        """
        return self._help_text
    
    def SetHelp(self, text):
        """ Sets the help text for the action.

        """
        self._help_text = text
        menu_item = self._menu_item
        if menu_item is not None:
            menu_item.SetHelp(text)

    def IsSeparator(self):
        """ Returns whether or not this action is a separator.

        """
        return self._separator

    def SetSeparator(self, separator):
        """ Sets whether or not this action is a separator.

        """
        # If the menu item has already been created, it needs
        # be removed from the parent and re-installed since 
        # the separator state cannot be changed in-place.
        self._separator = separator
        menu_item = self._menu_item
        if menu_item is not None:
            parent = self._parent()
            if parent is not None:
                idx = parent.GetMenuItems().index(menu_item)
                parent.Remove(menu_item.GetId())
                self.Install(idx)

    def IsCheckable(self):
        """ Returns whether or not the action is checkable.

        """
        return self._checkable
    
    def SetCheckable(self, checkable):
        """ Sets whether or not the action is checkable.

        """
        # If the menu item has already been created, it needs
        # be removed from the parent and re-installed since 
        # the checkable state cannot be changed in-place.
        self._checkable = checkable
        menu_item = self._menu_item
        if menu_item is not None:
            parent = self._parent()
            if parent is not None:
                idx = parent.GetMenuItems().index(menu_item)
                parent.Remove(menu_item.GetId())
                self.Install(idx)

    def IsChecked(self):
        """ Returns whether or not the action is checked. This only
        has semantic meaning if the action is also checkable.

        """
        return self._checked
    
    def SetChecked(self, checked):
        """ Sets whether or not the action is checked. This only has
        semantic meaning if the action is also checkable.

        """
        self._checked = checked
        menu_item = self._menu_item
        if menu_item is not None and self._checkable:
            menu_item.Check(checked)

    def Enable(self, enabled):
        """ Enables or disables the action.

        """
        self._enabled = enabled
        menu_item = self._menu_item
        if menu_item is not None:
            menu_item.Enable(enabled)

    def Destroy(self):
        """ A destructor method which removes the menu item from its
        parent before destroying the item and itself.

        """
        if self:
            menu_item = self._menu_item
            parent = self._parent()
            if menu_item is not None and parent is not None:
                try:
                    # This will raise a ValueError if the menu item is
                    # not in the list. Looping over the list and checking
                    # for equality won't work; a wx-ism
                    parent.GetMenuItems().index(menu_item)
                except ValueError:
                    pass
                else:
                    parent.Remove(menu_item.GetId())

            if menu_item:
                menu_item.Destroy()
            self.menu_item = None

            # Before destroying the action, we need to unbind the event
            # handler, or it will continue being called for every 
            # menu event which will result in PyDeadObject errors.
            binder = self._binder()
            if binder is not None:
                binder.Unbind(wx.EVT_MENU, handler=self.OnMenuEvent)
            super(wxEnamlAction, self).Destroy()

    def Freeze(self):
        """ An api compatibility method. This is a no-op since actions
        cannot be frozen or thawed.

        """
        pass

    def Thaw(self):
        """ An api compatibility method. This is a no-op since actions
        cannot be frozen or thawed.

        """
        pass
        

class WXAction(WXComponent, AbstractTkAction):
    """ A wx implementation of Action.

    """
    #--------------------------------------------------------------------------
    # Setup Methods
    #--------------------------------------------------------------------------
    def create(self, parent):
        """ Creates the underlying QAction object.

        """
        self.widget = wxEnamlAction(parent)

    def initialize(self):
        """ Initializes the underlying QAction object.

        """
        super(WXAction, self).initialize()
        shell = self.shell_obj
        self.set_text(shell.text)
        self.set_checkable(shell.checkable)
        self.set_checked(shell.checked)
        self.set_status_tip(shell.status_tip)
        self.set_tool_tip(shell.tool_tip)
        self.set_description(shell.description)
        self.set_separator(shell.separator)
        
    def bind(self):
        """ Binds the event handlers for the underlying QAction object.

        """
        super(WXAction, self).bind()
        self.widget.Bind(EVT_ACTION_TRIGGERED, self.on_triggered)
        self.widget.Bind(EVT_ACTION_TOGGLED, self.on_toggled)

    #--------------------------------------------------------------------------
    # Change Handlers 
    #--------------------------------------------------------------------------
    def shell_text_changed(self, text):
        """ The change handler for the 'text' attribute on the shell
        object.

        """
        self.set_text(text)
    
    def shell_checkable_changed(self, checkable):
        """ The change handler for the 'checkable' attribute on the 
        shell object.

        """
        self.set_checkable(checkable)
    
    def shell_checked_changed(self, checked):
        """ The change handler for the 'checked' attribute on the
        shell object.

        """
        self.set_checked(checked)

    def shell_status_tip_changed(self, status_tip):
        """ The change handler for the 'status_tip' attribute on the 
        shell object.

        """
        self.set_status_tip(status_tip)
    
    def shell_tool_tip_changed(self, tool_tip):
        """ The change handler for the 'tool_tip' attribute on the 
        shell object.

        """
        self.set_tool_tip(tool_tip)
    
    def shell_description_changed(self, description):
        """ The change handler for the 'description' attribute on the 
        shell object.

        """
        self.set_description(description)

    def shell_separator_changed(self, separator):
        """ The change handler for the 'separator' attribute on the
        shell object.

        """
        self.set_separator(separator)

    #--------------------------------------------------------------------------
    # Signal Handlers
    #--------------------------------------------------------------------------
    def on_triggered(self, event):
        """ A signal handler for the 'triggered' signal of the QAction.

        """
        self.shell_obj.triggered()

    def on_toggled(self, event):
        """ A signal handler for the 'toggled' signal of the QAction.

        """
        shell = self.shell_obj
        shell.checked = self.widget.IsChecked()
        shell.toggled()

    #--------------------------------------------------------------------------
    # Widget Update Methods 
    #--------------------------------------------------------------------------
    def set_text(self, text):
        """ Sets the text of the action.

        """
        self.widget.SetText(text)

    def set_checkable(self, checkable):
        """ Sets whether or not the action is checkable.

        """
        self.widget.SetCheckable(checkable)
    
    def set_checked(self, checked):
        """ Sets whether or not the action is checked.

        """
        self.widget.SetChecked(checked)

    def set_status_tip(self, status_tip):
        """ Sets the status tip text for the action.

        """
        self.widget.SetHelp(status_tip)
    
    def set_tool_tip(self, tool_tip):
        """ Sets the tool tip text for the action.

        """
        #self.widget.setToolTip(tool_tip)
    
    def set_description(self, description):
        """ Sets the description text for the action.

        """
        #self.widget.setWhatsThis(description)

    def set_separator(self, separator):
        """ Sets whether or not the QAction is a separator.

        """
        self.widget.SetSeparator(separator)

