import os

qt_api = os.environ.get('QT_API', 'pyside').lower()

if qt_api == 'pyside':
    from PySide import QtCore, QtGui
    
elif qt_api == 'pyqt' or qt_api == 'pyqt4':
    # make things PySide compatible
    import sip
    sip.setapi('QString', 2)
    sip.setapi('QVariant', 2)
    
    from PyQt4 import QtCore, QtGui

else:
    # shouldn't happen since we currently default to pyside, but we could get garbage environment
    raise ValueError('Invalid QT_API: %s' % qt_api)
