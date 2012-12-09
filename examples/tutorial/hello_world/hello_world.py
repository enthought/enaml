#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import enaml
from enaml.stdlib.sessions import show_simple_view


if __name__ == '__main__':
    with enaml.imports():
        from hello_world_view import Main

    main_view = Main()
    show_simple_view(main_view)

