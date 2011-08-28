import weakref

import wx

from traits.api import implements, HasStrictTraits, Instance, Str

from ..mixins.meta_info_mixin import MetaInfoMixin

from ..i_component import IComponent


class WXComponent(HasStrictTraits, MetaInfoMixin):
    """ A wxPython implementation of IComponent.

    A WXComponent is not meant to be used directly. It provides some 
    common functionality that is useful to all widgets and should 
    serve as the base class for all other classes.

    Attributes
    ----------
    widget : Instance(wx.Object)
        The underlying wx widget for this component.

    parent_ref : Instance(weakref.ref) or None
        A weak reference to the parent component of this component.

    Methods
    -------
    parent_sizer()
        Returns the sizer for the parent component or None.

    parent_widget()
        Returns the logical wx.Window parent for this component. Since
        some parents may wrap non-Window objects (like sizers), this
        method will walk up the tree of parent components until a 
        wx.Window is found or None if no Window is found.

    See Also
    --------
    IComponent

    """
    implements(IComponent)

    #===========================================================================
    # IComponent interface
    #===========================================================================
    name = Str

    def toolkit_widget(self):
        """ Returns the toolkit specific widget for this component.

        """
        return self.widget

    def parent(self):
        """ Returns a strong reference to the parent component or None.

        """
        return self.parent_ref() if self.parent_ref is not None else None

    # The rest of the IComponent interface comes from MetaInfoMixin

    #===========================================================================
    # Implementation
    #===========================================================================
    widget = Instance(wx.Object)

    parent_ref = Instance(weakref.ref)

    def set_parent(self, parent):
        """ Store a weakref to the given parent.

        This is a convienence method to be used during layout in 
        order to store a weakref to the provided parent. The strong
        ref to the parent can be retrieved by calling the 'parent'
        method. This method is called by the 'layout' method of
        various components and is not meant for public consumption.

        Arguments
        ---------
        parent : Either(IPanel, IContainer)
            The parent component for this component.

        Returns
        -------
        None

        """
        self.parent_ref = weakref.ref(parent) if parent is not None else None
        
    def parent_sizer(self):
        """ Returns the sizer for the parent component or None.

        If the actual parent wraps a wx.Sizer, then that sizer is 
        returned. If the actual parent wraps a wx.Window, then the
        sizer of that window is returned if one exists. In all 
        other cases, this method returns None.

        Arguments
        ---------
        None

        Returns
        -------
        result : wx.Sizer or None

        """
        parent = self.parent()
        if parent:
            widget = parent.widget
            if widget:
                if isinstance(widget, wx.Sizer):
                    return widget
                elif isinstance(widget, wx.Window):
                    return widget.GetSizer()
                else:
                    return None

    def parent_widget(self):
        """ Returns the logical wx.Window parent for this component. 

        Since some parents may wrap non-Window objects (like sizers), 
        this method will walk up the tree of parent components until a 
        wx.Window is found or None if no Window is found.

        Arguments
        ---------
        None

        Returns
        -------
        result : wx.Window or None

        """
        parent = self.parent()
        while parent:
            widget = parent.widget
            if isinstance(widget, wx.Window):
                return widget
            parent = parent.parent()

