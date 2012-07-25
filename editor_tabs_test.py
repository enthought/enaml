import enaml
from enaml.qt.qt_local_application import QtLocalApplication

app = QtLocalApplication()

with enaml.imports():
    from editor_tabs_test import Main
    view = Main()

app.serve('main', view)

app.mainloop()
