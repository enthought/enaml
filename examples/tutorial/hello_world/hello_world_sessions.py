#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import enaml
from enaml.stdlib.sessions import simple_session


if __name__ == '__main__':
    with enaml.imports():
        from hello_world_view import Main

    sess_one = simple_session('hello-world', 'A hello world example', Main)
    sess_two = simple_session(
        'hello-world-python', 'A customized hello world example',
        Main, message="Hello, world, from Python!"
    )

    from enaml.qt.qt_application import QtApplication
    app = QtApplication([sess_one, sess_two])
    app.start_session('hello-world')
    app.start_session('hello-world-python')
    app.start()
