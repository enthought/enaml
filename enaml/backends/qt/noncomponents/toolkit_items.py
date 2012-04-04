#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt_dock_manager import QtDockManager
from .qt_icon import QtIcon
from .qt_image import QtImage


TOOLKIT_ITEMS = {
    'DockManager': QtDockManager,
    'Image': QtImage,
    'Icon': QtIcon,
}

