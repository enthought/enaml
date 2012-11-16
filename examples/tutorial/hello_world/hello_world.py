#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import enaml
from enaml.stdlib.sessions import simple_app
from enaml.qt.qt_local_server import QtLocalServer


if __name__ == '__main__':
    with enaml.imports():
        from hello_world_view import Main

    app = simple_app(
        'main', 'A customized hello world example', Main,
        message="Hello, world, from Python!"
    )

    server = QtLocalServer(app)
    client = server.local_client()
    client.start_session('main')
    server.start()

