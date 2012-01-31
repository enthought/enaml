#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import enaml

with enaml.imports():
    from hello_world_view import MyMessageToTheWorld

view = MyMessageToTheWorld(message="Hello, world!")
view.show()

