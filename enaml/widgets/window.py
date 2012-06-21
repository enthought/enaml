#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Instance, Unicode, on_trait_change, Tuple, Range

from enaml.async.async_application import AbstractBuilder, AsyncApplication
from .messenger_widget import MessengerWidget


class Window(MessengerWidget):
    """ A top-level Window component.

    A Window component is represents of a top-level visible component
    with a frame decoration. It may have at most one child widget which
    is expanded to fit the size of the window. It does not support
    features like MenuBars or DockPanes, for that, use a MainWindow.

    """
    #: The titlebar text.
    title = Unicode

    #: The titlebar icon.
    # XXX needs to be implemented
    #icon = Instance()

    #: The initial size to set the window on the first call show()
    #: If the initial size is set to (-1, -1), then a default value
    #: will be computed more-or-less intelligently. This attribute
    #: is only used the first time the window is shown to the screen.
    #: Further changes to the attribute will have no effect. The
    #: constituent values must be >= -1. The default is (-1, -1).
    initial_size = Tuple(Range(-1), Range(-1))
    
    #: The initial size of the window to use if the attempt to compute
    #: one intelligently fails. This is the "last resort" of determining
    #: the initial size. The constituent values must be >= 0. The 
    #: default is (200, 100).
    initial_size_default = Tuple(Range(0, value=200), Range(0, value=100))

    #: The minimum size allowable for the window. If the min size is 
    #: set to (-1, -1), then the minimum will be computed based on
    #: the children of the window, and in such cases the minimum size
    #: that is in use can be retrieved with the min_size() method.
    #: The constituent values must be >= -1. The default is (-1, -1).
    minimum_size = Tuple(Range(-1), Range(-1))

    #: The minimum size of the window to use if the attempt to compute
    #: one intelligently fails. This is the "last resort" of determining
    #: the minimum size. The constituent values must be >= 0. The 
    #: default is (0, 0).
    minimum_size_default = Tuple(Range(0), Range(0))

    #: The maximum size allowable for the window. If the max size is 
    #: set to (-1, -1), then the maximum will be computed based on
    #: the children of the window, and in such cases the maximum size
    #: that is in use can be retrieved with the max_size() method.
    #: The consituent values must be >= -1. The default is (-1, -1).
    maximum_size = Tuple(Range(-1), Range(-1))

    #: The maximum size of the window to use if the attempt to compute
    #: one intelligently fails. This is the "last resort" of determining
    #: the minimum size. The constituent values must be >= 0. The 
    #: default is (2**24 - 1, 2**24 - 1)
    maximum_size_default = Tuple(Range(0, value=(2**24 - 1)), 
                                 Range(0, value=(2**24 - 1)))

    #: The private storage for the widget tree builder. A reference must
    #: be kept to the builder, since the lifetime of the implementation
    #: widgets is tied to the lifetime of the builder.
    _builder = Instance(AbstractBuilder)

    #--------------------------------------------------------------------------
    # Initialization
    #--------------------------------------------------------------------------
    def initial_attrs(self):
        super_attrs = super(Window, self).initial_attrs()
        attrs = {
            'title' : self.title,
            #'icon' : self.icon,
            'initial_size' : self.initial_size,
            'initial_size_default' : self.initial_size_default,
            'minimum_size' : self.minimum_size,
            'minimum_size_default' : self.minimum_size_default,
            'maximum_size' : self.maximum_size,
            'maximum_size_default' : self.maximum_size_default
        }
        super_attrs.update(attrs)
        return super_attrs

    def bind(self):
        super(Window, self).bind()
        self.default_send_attr_bind(
            'title', 'initial_size', 'minimum_size', 'maximum_size',
            'initial_size_default', 'minimum_size_default',
            'maximum_size_default'
        )

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def maximize(self):
        """ Send a 'maximize' command to the client UI.

        """
        self.send('maximize', {})

    def minimize(self):
        """ Send a 'minimize' command to the client UI.

        """
        self.send('minimize', {})

    def restore(self):
        """ Send a 'restore' command to the client UI.

        """
        self.send('restore', {})

    def show(self):
        """ Build the UI tree for this window and tell the client to show it.

        """
        if not self.initialized:
            self.initialize()
        builder = self._builder
        if builder is None:
            builder = self._builder = AsyncApplication.instance().builder()
            build_info = self.build_info()
            builder.build(build_info)
        self.send('show', {})

    

