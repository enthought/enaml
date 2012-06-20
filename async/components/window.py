#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Unicode, on_trait_change, Instance

from ..core.messenger_widget import MessengerWidget
from ..core.async_application import AbstractBuilder, AsyncApplication


class Window(MessengerWidget):

    title = Unicode

    _builder = Instance(AbstractBuilder)

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

