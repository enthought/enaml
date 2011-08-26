from traits.api import Instance, Dict, HasTraits

from ..meta.base import BaseMetaInfo
from ..meta.i_meta_handler import IMetaHandler


class MetaInfoMixin(HasTraits):
    """ A mixin class for meta info objects.
    
    This mixin class provides some common toolkit independent base
    handling of IMetaInfo objects required by the IComponent interface.
    
    Attributes
    ----------
    meta_handlers : Dict(IMetaInfo, IMetaInfoHandler)
        Storage for the created meta info handlers.

    Methods
    -------
    add_meta_info(meta_info)
        See also IComponent.add_meta_info

    remove_meta_info(meta_info)
        See also IComponent.remove_meta_info

    """
    meta_handlers = Dict(BaseMetaInfo, IMetaHandler)

    def add_meta_info(self, meta_info, autohook=True):
        """ Add an IMetaInfo object to this component.
        
        We don't know in advance what kinds of meta objects will
        be defined, especially by the user. So, we dispatch to 
        specially named methods that subclasses can optionally define 
        in order to create handlers for the meta objs.

        The method pattern is of the form '_meta_handler_<name>'
        where <name> is the type name of the meta info object.
        The methods should take a single argument, which is the
        meta info object itself, and return an IMetaInfoHandler 
        instance for this meta info object.

        See Also
        --------
        IComponent.add_meta_info

        """
        handlers = self.meta_handlers

        if meta_info in handlers:
            msg = 'MetaInfo obj %s has already been added.' % meta_info
            raise ValueError(msg)
        
        name = '_meta_handler_%s' % meta_info.__class__.__name__
        handler = getattr(self, name, self._meta_handler_default)(meta_info)
        handlers[meta_info] = handler
        
        if handler and autohook:
            handler.hook()

    def remove_meta_info(self, meta_info):
        """ Remove an IMetaInfo object from this componentself.

        This method will remove and teardown a meta info handler
        for the given meta info object.

        See Also
        --------
        IComponent.remove_meta_obj

        """
        handlers = self.meta_handlers
        
        if meta_info not in handlers:
            msg = 'Meta info obj %s has not been added.' % meta_info
            raise ValueError(msg)
        
        handler = handlers.pop(meta_info)
        if handler:
            handler.unhook()

    def get_meta_handler(self, meta_info):
        """ Return the IMetaHandler for this meta_info object.

        This method will get and return the meta handler for the 
        provided meta info object. Or raise an error if it hasn't
        yet been added.

        See Also
        --------
        IComponent.get_meta_handler

        """
        handlers = self.meta_handlers

        if meta_info not in handlers:
            msg = 'Meta info obj %s has not been added.' % meta_info
            raise ValueError(msg)
        
        return handlers[meta_info]
        
    def _meta_handler_default(self, meta_info):
        """ A default meta info handler that just returns None.

        """
        return None

