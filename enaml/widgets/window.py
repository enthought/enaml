#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Instance, Unicode, on_trait_change

from ..core.messenger_widget import MessengerWidget
from ..core.async_application import AbstractBuilder, AsyncApplication


class Window(MessengerWidget):
    """ A top-level Window component.

    A Window component is represents of a top-level visible component
    with a frame decoration. It may have at most one child widget which
    is expanded to fit the size of the window. It does not support
    features like MenuBars or DockPanes, for that, use a MainWindow.

    """
    #: The titlebar text.
    title = Unicode

    #: The widget tree builder
    _builder = Instance(AbstractBuilder)

    #--------------------------------------------------------------------------
    # Toolkit Communication
    #--------------------------------------------------------------------------
    def initial_attrs(self):
        super_attrs = super(Window, self).initial_attrs()
        super_attrs.update(title=self.title)
        return super_attrs

    @on_trait_change('title')
    def sync_object_state(self, name, new):
        msg = 'set_' + name
        self.send(msg, {'value': new})

    def show(self):
        builder = self._builder
        if builder is None:
            builder = self._builder = AsyncApplication.instance().builder()
            build_info = self.build_info()
            builder.build(build_info)
        self.send('show', {})

