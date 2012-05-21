#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import enaml

with enaml.imports():
    from hello_world_view import Main

view = Main(message="Hello, world, from Python!")
view.show()

