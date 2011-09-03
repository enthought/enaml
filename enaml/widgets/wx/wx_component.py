import wx

from traits.api import implements, HasStrictTraits, WeakRef, Instance

from ..component import IComponentImpl


class WXComponent(HasStrictTraits):
    """ A wxPython implementation of Component.

    A WXComponent is not meant to be used directly. It provides some 
    common functionality that is useful to all widgets and should 
    serve as the base class for all other classes.

    See Also
    --------
    Component

    """
    implements(IComponentImpl)

    #---------------------------------------------------------------------------
    # IComponentImpl interface
    #---------------------------------------------------------------------------
    parent = WeakRef

    def toolkit_widget(self):
        """ Returns the toolkit specific widget for this component.

        """
        return self.widget
    
    def parent_name_changed(self, name):
        """ WXComponent doesn't care about the name. Subclasses should
        reimplement if they need that info.

        """
        pass

    #---------------------------------------------------------------------------
    # Implementation
    #---------------------------------------------------------------------------
    widget = Instance(wx.Object)
        
    def parent_widget(self):
        """ Returns the logical wx.Window parent for this component. 

        Since some parents may wrap non-Window objects (like sizers), 
        this method will walk up the tree of parent components until a 
        wx.Window is found or None if no wx.Window is found.

        Arguments
        ---------
        None

        Returns
        -------
        result : wx.Window or None

        """
        # Our parent is a Compent, and the parent of 
        # a Component is also a Component
        parent = self.parent
        while parent:
            widget = parent.toolkit_widget()
            if isinstance(widget, wx.Window):
                return widget
            parent = parent.parent
        
    def child_widgets(self):
        """ Iterates over the parent's children and yields the 
        toolkit widgets for those children.

        """
        for child in self.parent.children:
            yield child.toolkit_widget()


