from traits.api import Interface, Instance

from .i_meta_info import IComponent, IMetaInfo


class IMetaHandler(Interface):

    meta_info = Instance(IMetaInfo)

    component = Instance(IComponent)

    def setup(self):
        raise NotImplementedError

    def teardown(self):
        raise NotImplementedError

