#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import enaml
from enaml.application import Application
from enaml.stdlib.sessions import view_handler
from enaml.qt.qt_local_server import QtLocalServer

if __name__ == '__main__':
    with enaml.imports():
        from hello_world_view import Main

    main_handler = view_handler(Main)
    app = Application([
        main_handler('hello-world', 'A hello world example'),
        main_handler('hello-world-python', 'A hello world example',
            message="Hello, world, from Python!")
    ])

    server = QtLocalServer(app)
    client = server.local_client()
    client.start_session('hello-world')
    client.start_session('hello-world-python')
    server.start()
