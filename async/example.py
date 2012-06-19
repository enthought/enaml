from PySide.QtGui import *
from PySide.QtCore import *

from command_reply import AsyncCommand


class Application(QApplication):

    process = Signal(object)

    def __init__(self):
        super(Application, self).__init__([])
        self.widgets = {}
        self.process.connect(self.on_process, Qt.QueuedConnection) # this makes things async

    def register(self, wid, widget):
        self.widgets[wid] = widget

    def send(self, wid, cmd, ctxt):
        w = self.widgets.get(wid)
        if w is not None:
            acmd = AsyncCommand()
            items = (w, cmd, ctxt, acmd)
            self.process.emit(items)
            return acmd

    @Slot(object)
    def on_process(self, items):
        widget, cmd, ctxt, reply = items
        res = widget.receive(cmd, ctxt)
        reply.finished(res)


app = Application()


class Slider(QSlider):

    def __init__(self, parent):
        super(Slider, self).__init__(parent)
        self.valueChanged.connect(self.on_change)

    def on_change(self):
        ac = app.send('label', 'update_text', {'text': str(self.value())})
        ac.add_callback(self.notify)

    def notify(self, ac, res):
        print "command finished", res


class Label(QLabel):

    def __init__(self, parent):
        super(Label, self).__init__(parent)
        app.register('label', self)
        self.setText('Label')

    def receive(self, cmd, ctxt):
        mn = 'receive_' + cmd
        mth = getattr(self, mn, None)
        if mth is not None:
            return mth(ctxt)

    def receive_update_text(self, ctxt):
        self.setText(ctxt['text'])
        return 'succes'


w = QWidget()
s = Slider(w)
l = Label(w)

hl = QHBoxLayout()
hl.addWidget(l)
hl.addWidget(s)
w.setLayout(hl)

w.show()

app.exec_()

