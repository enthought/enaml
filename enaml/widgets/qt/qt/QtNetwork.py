#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from . import qt_api

if qt_api == 'pyqt':
    from PyQt4.QtNetwork import *
    
else:
    from PySide.QtNetwork import *
