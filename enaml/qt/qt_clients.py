#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
def window_importer():
    from .qt_window import QtWindow
    return QtWindow


CLIENTS = {
    'Window': window_importer
}

