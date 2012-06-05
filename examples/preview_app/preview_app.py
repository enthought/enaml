#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
""" The entry point launcher for the Enaml Preview application.

"""
import enaml

from preview_config import ViewConfig


if __name__ == '__main__':
    config = ViewConfig()
    with enaml.imports():
        from viewer import PreviewMain
    view = PreviewMain(view_config=config)
    view.show()

