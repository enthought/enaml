#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import enaml
from enaml.application import Application
from enaml.stdlib.sessions import simple_session
from enaml.qt.qt_local_server import QtLocalServer


if __name__ == '__main__':
    with enaml.imports():
        from hello_world_view import Main

    sess_one = simple_session('hello-world', 'A hello world example', Main)
    sess_two = simple_session(
        'hello-world-python', 'A customized hello world example',
        Main, message="Hello, world, from Python!"
    )

    app = Application([sess_one, sess_two])

    server = QtLocalServer(app)
    client = server.local_client()
    client.start_session('hello-world')
    client.start_session('hello-world-python')
    server.start()

