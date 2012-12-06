#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import logging
from urlparse import urlparse
from weakref import ref

from enaml.utils import id_generator

from .qt.QtGui import QImage
from .q_deferred_caller import deferredCall


logger = logging.getLogger(__name__)


#: An id generator for making requests to the server.
req_id_generator = id_generator('r_')


class DeferredResource(object):
    """ An deferred resource object returned by a `QtURLRequestManager`.

    Instances of this class are provided to widgets when they request a
    resource url. Since the url may need to be retrieved from a server,
    Loading occurs asynchronously. This object allows a widget to supply
    a callback to be invoked when the resource is loaded.

    """
    __slots__ = ('_callback')

    def __init__(self):
        """ Initialize a DeferredResource.

        """
        self._callback = None

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _notify(self, resource):
        """ Notify the consumer that the resource is available.

        This method is invoked directly by a `QtURLRequestManager`. It
        should not be called by user code.

        Parameters
        ----------
        resource : object
            An object of the appropriate type for the requested resource.

        """
        callback = self._callback
        self._callback = None
        if callback is not None:
            callback(resource)

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def on_load(self, callback):
        """ Register a callback to be invoked on resource load.

        Parameters
        ----------
        callback : callable
            A callable which accepts a single argument, which is the
            resource object loaded for the requested resource.

        """
        self._callback = callback


class QtURLManager(object):
    """ An object which manages requesting urls from the server session.

    """
    def __init__(self, session):
        """ Initialize a QtURLRequestManager.

        Parameters
        ----------
        session : QtSession
            The QtSession object which owns this manager. Only a weak
            reference to the session is maintained.

        """
        self._session = ref(session)
        self._handles = {}
        self._pending = {}

    def load(self, url, **kwargs):
        """ Loade the resource handle for the given url.

        This method will asynchronously load the resource for the given
        url, requesting it from the server side session if needed.

        Parameters
        ----------
        url : str
            The url pointing to the resource to load.

        **kwargs
            Addition metadata required to load the resource of the
            given type. See the individual load handlers for the
            supported keywords.

        Returns
        -------
        result : DeferredResource
            A deferred resource object which will invoke a callback on
            resource load.

        """
        scheme = urlparse(url).scheme
        handler = getattr(self, '_load_' + scheme, None)
        if handler is None:
            msg = 'unhandled request scheme for url: `%s`'
            logger.error(msg % url)
            return DeferredResource()
        return handler(url, **kwargs)

    def on_reply(self, content):
        """ Handle the reply for a previously sent url request.

        This method is called by the QtSession object when it receives
        an `url_reply` action. It should not be called directly by
        user code.

        Parameters
        ----------
        content : dict
            The content dictionary sent with the action.

        """
        url = content['url']
        scheme = urlparse(url).scheme
        handler = getattr(self, '_%s_reply' % scheme, None)
        if handler is None:
            msg = 'unhandled reply scheme for url: `%s`'
            logger.error(msg % url)
            return
        handler(content)

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _load_image(self, url, size=(-1, -1)):
        """ Load an image resource.

        Parameters
        ----------
        url : str
            The url pointing to the image to load.

        size : tuple, optional
            The requested size for the image. The default is (-1, -1)
            and indicates that the image should be loaded using its
            natural size.

        Returns
        -------
        result : DeferredResourceLoader or None
            A deferred loader object which will invoke a callback on
            resource load. None will be returned if the session object
            has been destroyed.

        """
        loader = DeferredResource()
        key = (url, size)
        handles = self._handles
        if key in handles:
            deferredCall(loader._notify, handles[key])
            return loader
        pending = self._pending
        if key in pending:
            pending[key].append(loader)
            return loader
        session = self._session()
        if session is not None:
            req_id = req_id_generator.next()
            pending[req_id] = key
            pending[key] = [loader]
            content = {}
            content['id'] = req_id
            content['url'] = url
            content['size'] = size
            session.send(session._session_id, 'url_request', content)
        return loader

    def _image_reply(self, content):
        """ Handle the url reply for an image request.

        Parameters
        ----------
        content : dict
            The content dictionary sent with the 'url_reply' action.

        """
        # XXX hack to get up and running, needs more checks + features
        req_id = content['id']
        status = content['status']
        pending = self._pending
        key = pending.pop(req_id)
        loaders = pending.pop(key)
        if status == 'ok':
            img = QImage.fromData(content['data'])
            self._handles[key] = img
            for loader in loaders:
                loader._notify(img)

