from traits.api import Interface, Instance

from .i_component import IComponent
from .i_meta_info import IMetaInfo


class IMetaHandler(Interface):

    meta_info = Instance(IMetaInfo)

    component = Instance(IComponent)

    def setup(self):
        raise NotImplementedError

    def teardown(self):
        raise NotImplementedError

