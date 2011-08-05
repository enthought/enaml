""" Mixins useful for creating QWidget subclasses with
custom behavior.

"""
from PySide import QtCore


class ResizeEventMixin(object):
    """ This mixin class implements the resizeEvent handler and
    converts that event into a signal with name `resized`. 
    The event object will be passed along with the signal.

    """
    resized = QtCore.Signal(QtCore.QEvent)

    def resizeEvent(self, evt):
        super(ResizeEventMixin, self).resizeEvent(evt)
        self.resized.emit(evt)


class MoveEventMixin(object):
    """ This mixin class implements the moveEvent handler and
    converts that event into a signal with name `moved`. 
    The event object will be passed along with the signal.

    """
    moved = QtCore.Signal(QtCore.QEvent)

    def moveEvent(self, evt):
        super(MoveEventMixin, self).moveEvent(evt)
        self.moved.emit(evt)



class SizeHintMixin(object):
    """ A mixin for setting the size hint on the widget.

    The mixin provides the method: sizeHint() which is used by Qt.

    There is also a property size_hint which should be set whenever
    the sizeHint needs to change.

    This mixin class must be inherited before the QWidget class 
    in order to work properly.

    """
    _size_hint = (-1, -1)

    def sizeHint(self):
        size_hint = self.size_hint
        if size_hint == (-1, -1):
            size_hint = super(SizeHintMixin, self).sizeHint()
        else:
            size_hint = QtCore.QSize(*size_hint)
        return size_hint
    
    @property
    def size_hint(self):
        return self._size_hint

    @size_hint.setter
    def size_hint(self, val):
        self._size_hint = val
        self.updateGeometry()


class GeneralWidgetMixin(ResizeEventMixin, MoveEventMixin, SizeHintMixin):
    """ A combination of the resize, move, and size policy mixin classes.

    This provides the basic functionality that should be added for 
    all widgets so that their behavior is appropriately customizable.
    
    It must be inherited before any QWidget class.
    """
    pass


