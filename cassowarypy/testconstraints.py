
#
#           |<--- space --->|
#           |               |
#  0 ----- x1 ---- x2 ----- x3 ----- width
#  |                                     |
#  |<----------- parent width ---------->|
#
# eq 1: (x1 + x3) / 2 - x2 = 0
# eq 2: x2 * 3 - width = 0
# eq 3: 10 * x2 - 10 * x1 - width = 0
#
# matrix form:
# [  0.5, -1.0, 0.5, 0.0] | x1 |   |   0    |   | 0 |
# [  0.0,  3.0, 0.0, 0.0] | x2 | - | width  | = | 0 |
# [ -5.0,  5.0, 0.0, 0.0] | x3 |   | width  |   | 0 |
# [  0.0,  0.0, 0.0, 2.0] |  y | - | height |   | 0 |
#
# constraints:
# 
# x1 < x3
#
# x1 > 0
# 
# x3 < width
#
#

if __name__ == '__main__':
    from PySide import QtGui, QtCore
    import csw

    app = QtGui.QApplication([])
    
    class ResizingFrame(QtGui.QWidget):
        resized = QtCore.Signal()

        def resizeEvent(self, event):
            self.resized.emit()
        
    f = ResizingFrame()
    b = QtGui.QPushButton(f)
    b.setText('Foo')
    b.resize(50, 50)
    fw = csw.Variable('fw')
    fh = csw.Variable('fh')

    bx = csw.Variable('bx')
    by = csw.Variable('by')
    #bw = csw.Variable('bw')
    #bh = csw.Variable('bh')

    solver = csw.SimplexSolver()
    solver.AddConstraint(csw.LinearEquation(bx, fw / 2.0))
    solver.AddConstraint(csw.LinearEquation(by, fh / 2.0))
    solver.AddConstraint(csw.LinearInequality(bx, csw.cnGEQ, 0.0))
    solver.AddConstraint(csw.LinearInequality(by, csw.cnGEQ, 0.0))

    def resolve():
        w, h = f.width(), f.height()
        solver.AddEditVar(fw)
        solver.AddEditVar(fh)
        solver.BeginEdit()
        solver.SuggestValue(fw, w)
        solver.SuggestValue(fh, h)
        solver.Resolve()
        x = bx.Value()
        y = by.Value()
        b.move(x, y)
        solver.EndEdit()
        

    f.resized.connect(resolve)

    f.show()
    app.exec_()
    import sys
    sys.exit()

from scipy.optimize import fmin_slsqp
import numpy as np


def get_args(width, height):
    coeffs = np.array([[ 0.5, -1.0, 0.5, 0.0],
                       [ 0.0,  3.0, 0.0, 0.0],
                       [-5.0,  5.0, 0.0, 0.0],
                       [ 0.0,  0.0, 0.0, 2.0]])
    consts = np.array([0., width, width, height])
    return coeffs, consts


def objective(x, coeffs, consts):
     res = ((np.dot(coeffs, x) - consts)**2).sum()
     return res


def f_ieq(x, coeffs, consts):
     x1, x2, x3, h = x
     return np.array([x3 - x1, x1, consts[-2] - x3])

import sys
tk = sys.argv[1]

if tk == 'qt':

    from PySide import QtGui

    class MyWidget(QtGui.QWidget):

        def resizeEvent(self, event):
            width = self.width()
            height = self.height()
            args = get_args(width, height)

            init = np.array([child.x() for child in self.children()] + [height])
            results = fmin_slsqp(objective, init, args=args, f_ieqcons=f_ieq, disp=False)

            results, y = results[:3], results[-1]
            for xpos, child in zip(results, self.children()):
                child.move(int(xpos), int(y))

    if __name__ == '__main__':
        app = QtGui.QApplication([])
        w = MyWidget()
        pb1 = QtGui.QPushButton('foo', w)
        pb2 = QtGui.QPushButton('bar', w)
        pb3 = QtGui.QPushButton('baz', w)
        w.show()
        app.exec_()
else:

    import wx

    class MyPanel(wx.Panel):

        def __init__(self, *args, **kwargs):
            super(MyPanel, self).__init__(*args, **kwargs)
            self.Bind(wx.EVT_SIZE, self.OnResize)
        
        def OnResize(self, event):     
            width, height = self.GetSize()
            args = get_args(width, height)

            init = np.array([child.GetPosition()[0] for child in self.GetChildren()] + [height])
            results = fmin_slsqp(objective, init, args=args, f_ieqcons=f_ieq, disp=False)

            results, y = results[:3], results[-1]
            for xpos, child in zip(results, self.GetChildren()):
                child.Move((int(xpos), int(y)))

    if __name__ == '__main__':
        app = wx.PySimpleApp()
        f = wx.Frame(None)
        p = MyPanel(f)
        pb1 = wx.Button(p, -1, 'foo')
        pb2 = wx.Button(p, -1, 'bar')
        pb3 = wx.Button(p, -1, 'baz')
        f.Show()
        app.MainLoop()
