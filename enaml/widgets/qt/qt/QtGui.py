#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from . import qt_api

if qt_api == 'pyqt':
    from PyQt4.Qt import QKeySequence, QTextCursor
    from PyQt4.QtGui import *
    
else:
    from PySide.QtGui import *
