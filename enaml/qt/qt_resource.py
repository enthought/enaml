#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import logging

from .qt.QtGui import QImage


logger = logging.getLogger(__name__)


def on_convert_Image(image):
    """ Convert the given resource dict into a QImage.

    Parameters
    ----------
    image : dict
        A dictionary representation of an Enaml Image.

    Returns
    -------
    result : QImage
        The QImage instance for the given Enaml image dict.

    """
    format = image['format']
    if format == 'auto':
        qimage = QImage.fromData(image['data'])
    else:
        qimage = QImage()
    return qimage


def convert_resource(resource):
    """ Convert a resource dict into a Qt resource handle.

    Parameters
    ----------
    resource : dict
        A dictionary representation of the Qt resource to create.

    Returns
    -------
    result : QObject or None
        An appropriate Qt object for the resource, or None if the
        resource could not be converted.

    """
    items = globals()
    name = resource['class']
    handler = items.get('on_convert_' + name)
    if handler is None:
        for name in resource['bases']:
            handler = items.get('load_' + name)
            if handler is not None:
                break
        if handler is None:
            msg = 'failed to create resource `%s:%s`'
            logger.error(msg % (resource['class'], resource['bases']))
            return
    return handler(resource)

