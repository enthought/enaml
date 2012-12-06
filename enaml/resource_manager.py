#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import logging
from urlparse import urlparse

from traits.api import HasTraits, Dict, Str

from .image_provider import ImageProvider


logger = logging.getLogger(__name__)


class ResourceManager(HasTraits):
    """ A class which manages resource loading for a `Session`.

    A `ResourceManager` is used by a `Session` object to load resources
    when a url resource request is made by a client session. Users work
    with the manager by assigning provider objects associated with a
    host name. For example, a user can provide an image for the url
    `image://filesystem/c:/foo/bar.png` by assigning an `ImageProvider`
    instace to the `image_providers` dict with the key `filesystem`.

    """
    #: A dict mapping provider location to image provider object. When
    #: a resource `image://foo/bar/baz` is requested, the image provider
    #: provider `foo` is use to request path `/bar/baz`.
    image_providers = Dict(Str, ImageProvider)

    def load(self, callback, url, **kwargs):
        """ Load a resource from the manager.

        Parameters
        ----------
        callback : callable
            A callable object which will be invoked with the loaded
            resource object, or None if the loading fails. It must be
            safe to invoke this callback from a thread.

        url : str
            The url pointing to the resource to load.

        **kwargs
            Addition metadata required to load the resource of the
            given type. See the individual loading handlers for the
            supported keywords.

        """
        scheme = urlparse(url).scheme
        handler = getattr(self, '_load_' + scheme, None)
        if handler is None:
            msg = 'unhandled url resource scheme: `%s`'
            logger.error(msg % url)
            callback(None)
            return
        handler(callback, url, **kwargs)

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _load_image(self, callback, url, size=(-1, -1)):
        """ Load an image resource.

        This is a private handler method called by the `load` method.
        It should not be called directly by user code.

        Parameters
        ----------
        callback : callable
            A callable object which will be invoked with an `Image`
            object, or None if the loading fails. It must be safe to
            invoke this callback from a thread.

        url : str
            The url pointing to the image to load.

        size : tuple, optional
            The requested size for the image. The default is (-1, -1)
            and indicates that the image should be loaded using its
            natural size.

        """
        spec = urlparse(url)
        provider = self.image_providers.get(spec.netloc)
        if provider is None:
            msg = 'no image provider registered for url: `%s`'
            logger.error(msg % url)
            callback(None)
            return
        provider.request_image(spec.path, size, callback)

