#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
""" An example of using images and image providers in Enaml.

"""
from os import listdir
from os.path import dirname, join, splitext

import enaml
from enaml.session import Session
from enaml.image_provider import ImageProvider, Image


ROOT = join(dirname(__file__), 'example_images')
PATHS = {}
for p in listdir(ROOT):
    name = splitext(p)[0]
    PATHS[name] = join(ROOT, p)


class MyImageProvider(ImageProvider):
    """ A custom image provider for the image example.

    """
    def request_image(self, path, size, callback):
        """ Request an image from this provider.

        Parameters
        ----------
        path : str
            The requested path of the image, with the provider prefix
            removed. For example, if the full image source path was:
            `image://myimages/yellowstone` then the path passed to
            this method will be `/yellowstone`.

        size : tuple
            A tuple of (width, height) which is the requested size of
            the image. If this value is (-1, -1), then the image should
            be loaded in its original size. Otherwise, the image should
            be loaded in the requested size if possible.

        callback : callable
            A callable which should be invoked when the image is loaded.
            It accepts a single argument, which is the loaded `Image`
            object. It is safe to invoke this callable from a thread.

        """
        p = PATHS.get(path.lstrip('/'))
        if p is not None:
            with open(p, 'rb') as f:
                data = f.read()
            image = Image(data=data)
        else:
            image = None
        callback(image)


class ImageSession(Session):
    """ A simple session object for the image example.

    """
    def on_open(self):
        """ Setup the windows and resources for the session.

        """
        self.resource_manager.image_providers['myimages'] = MyImageProvider()
        with enaml.imports():
            from images_view import ImagesView
        images = sorted(PATHS.keys())
        self.windows.append(ImagesView(images=images))


if __name__ == '__main__':
    from enaml.qt.qt_application import QtApplication
    app = QtApplication([ImageSession.factory('main')])
    app.start_session('main')
    app.start()

