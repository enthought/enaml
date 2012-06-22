#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
def window_importer():
    from .qt_window import QtWindow
    return QtWindow


def slider_importer():
    from .qt_slider import QtSlider
    return QtSlider


CLIENTS = {
    'Window': window_importer,
    'Slider': slider_importer,
}

