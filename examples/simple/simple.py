
from enthought.traits.api import HasTraits, Int, Float, Str 
from traitsml.view_factory import ViewFactory

class Model(HasTraits):
    name = Str
    age = Int
    weight = Float

model = Model(name='Billy Bob', age=25, weight=175.5)
view_factory = ViewFactory('./simple.tml')
view = view_factory('main_container', model=model)

#------------------------------------------------------------------------------
# App startup which will go away at some point
#------------------------------------------------------------------------------
start_app = False
from PySide import QtGui
if not QtGui.QApplication.instance():
    start_app = True
    app = QtGui.QApplication([])

view.show()

if start_app:
    QtGui.QApplication.instance().exec_()


#------------------------------------------------------------------------------
# Prints when app exits
#------------------------------------------------------------------------------
print model.name
print model.age
print model.weight


