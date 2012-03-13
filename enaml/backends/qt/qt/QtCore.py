#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from . import qt_api

if qt_api == 'pyqt':
    from PyQt4.QtCore import *

    from PyQt4.QtCore import pyqtProperty as Property
    from PyQt4.QtCore import pyqtSignal as Signal
    from PyQt4.QtCore import pyqtSlot as Slot
    from PyQt4.Qt import QCoreApplication
    from PyQt4.Qt import Qt

    __version__ = QT_VERSION_STR
    __version_info__ = tuple(map(int, QT_VERSION_STR.split('.')))

else:
    from PySide import __version__, __version_info__
    from PySide.QtCore import *
