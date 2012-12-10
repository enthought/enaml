#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
""" An example of using icons and icon providers in Enaml.

"""
from os.path import dirname, join

import enaml
from enaml.session import Session
from enaml.image_provider import Image
from enaml.icon_provider import IconProvider, Icon, IconImage


ROOT = join(dirname(__file__), 'example_icons')


class MyIconProvider(IconProvider):
    """ A custom icon provider for the icon example.

    """
    path_map = {
        '/seek-forward': 'media-seek-forward.png',
        '/seek-backward': 'media-seek-backward.png',
        '/left-justify': 'format-justify-left.png',
        '/right-justify': 'format-justify-right.png',
        '/center-justify': 'format-justify-center.png',
        '/align-justify': 'format-justify-fill.png',
        '/window-icon': 'weather-clear.png',
        '/close': 'process-stop.png',
    }

    def request_icon(self, path, callback):
        """ Load the requested icon.

        Parameters
        ----------
        path : str
            The requested path of the icon, with the provider prefix
            removed. For example, if the full icon source path was:
            'icon://myicons/window-icon' then the path passed to this
            method will be `/window-icon`.

        callback : callable
            A callable which should be invoked when the icon is loaded.
            It accepts a single argument, which is the loaded `Icon`
            object. It is safe to invoke this callable from a thread.

        """
        # The mapping from icon name -> path is hard coded here, but
        # a typical application will have a way to resolve these paths
        # at runtime.
        if path == '/play-pause':
            with open(join(ROOT, 'media-playback-start.png'), 'rb') as f:
                off_data = f.read()
            with open(join(ROOT, 'media-playback-pause.png'), 'rb') as f:
                on_data = f.read()
            off_image = Image(data=off_data)
            on_image = Image(data=on_data)
            off_icon_img = IconImage(image=off_image)
            on_icon_img = IconImage(image=on_image, state='on')
            icon = Icon(images=[off_icon_img, on_icon_img])
        else:
            pth = self.path_map.get(path)
            if pth is not None:
                with open(join(ROOT, pth), 'rb') as f:
                    data = f.read()
                image = Image(data=data)
                icon_img = IconImage(image=image)
                icon = Icon(images=[icon_img])
            else:
                icon = None
        callback(icon)


class IconSession(Session):
    """ A simple session object for the icon example.

    """
    def on_open(self):
        """ Setup the windows and resources for the session.

        """
        self.resource_manager.icon_providers['myicons'] = MyIconProvider()
        with enaml.imports():
            from icons_view import IconsView
        self.windows.append(IconsView())


if __name__ == '__main__':
    from enaml.qt.qt_application import QtApplication
    app = QtApplication([IconSession.factory('main')])
    app.start_session('main')
    app.start()

