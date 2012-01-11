#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import enaml

with enaml.imports():
    from hello_world import MyMessageToTheWorld

view = MyMessageToTheWorld("Hello, world!")
view.show()

