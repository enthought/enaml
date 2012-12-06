#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from weakref import ref


class ImageURLReply(object):
    """ A reply object for sending a loaded image to a client session.

    Instances of `ImageURLReply` are callable and can passed as the
    callback argument to the `load` method of a `ResourceManager`.

    """
    __slots__ = ('_session', '_req_id', '_url')

    def __init__(self, session, req_id, url):
        """ Initialize an ImageURLReply.

        Parameters
        ----------
        session : Session
            The session object for which the image is being loaded.

        req_id : str
            The identifier that was sent with the originating request.
            This identifier will be included in the response.

        url : str
            The url that was sent with the originating request. This
            url will be included in the response.

        """
        self._session = ref(session)
        self._req_id = req_id
        self._url = url

    def __call__(self, image):
        """ Send the reply to the client session.

        Parameters
        ----------
        image : Image or None
            The loaded image object, or None if loading failed.

        """
        session = self._session()
        if session is not None:
            reply = {'id': self._req_id, 'url': self._url}
            if image is None:
                reply['status'] = 'fail'
            else:
                reply['status'] = 'ok'
                reply['size'] = image.size
                reply['format'] = image.format
                reply['data'] = image.data
            session.send(session.session_id, 'url_reply', reply)

