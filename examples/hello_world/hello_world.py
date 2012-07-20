#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import enaml
from enaml.qt.qt_local_application import QtLocalApplication


if __name__ == '__main__':

    with enaml.imports():
        from hello_world_view import Main


    view = Main(message="Hello, world, from Python!")
    
    app = QtLocalApplication()
    app.serve('main', view)

    app.mainloop()

