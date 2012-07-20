#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import enaml
from enaml.qt.qt_local_application import QtLocalApplication


if __name__ == '__main__':

    with enaml.imports():
        from simple_view import MainView

    view = MainView()
    
    app = QtLocalApplication()
    app.serve('main', view)

    app.mainloop()

