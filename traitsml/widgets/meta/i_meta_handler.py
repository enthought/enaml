from traits.api import Interface, Instance

from .base import BaseMetaInfo

from ..i_component import IComponent


class IMetaHandler(Interface):

    meta_info = Instance(BaseMetaInfo)

    component = Instance(IComponent)

    def hook(self):
        raise NotImplementedError
        
    def unhook(self):
        raise NotImplementedError

