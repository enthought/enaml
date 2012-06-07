#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import Queue
import threading

from PySide.QtGui import QWidget, QPushButton, QApplication

from enaml.backends.qt.qt_application import DeferredCaller


#------------------------------------------------------------------------------
# Async Task
#------------------------------------------------------------------------------
class AsyncTask(object):

    def execute(self):
        pass


class SetattrTask(AsyncTask):

    def __init__(self, obj, name, value):
        self.args = (obj, name, value)

    def execute(self):
        setattr(*self.args)


class CallTask(AsyncTask):

    def __init__(self, callback, callobj, *args, **kwargs):
        self.callback = callback
        self.callobj = callobj
        self.args = args
        self.kwargs = kwargs

    def execute(self):
        res = self.callobj(*self.args, **self.kwargs)
        self.callback(res)


#------------------------------------------------------------------------------
# Toolkit Widgets
#------------------------------------------------------------------------------
class ToolkitWidgetWrapper(object):
    
    def __init__(self, owner, toolkit):
        self.owner = owner
        self.widget = None
        self.toolkit = toolkit

    def post(self, task):
        self.toolkit.app.post_to_main(self, task)


class QtWidgetWrapper(ToolkitWidgetWrapper):
    
    def create(self, parent):
        pass

    def initialize(self):
        pass

    def bind(self):
        pass


class QtWindow(QtWidgetWrapper):
    
    def create(self, parent):
        self.widget = QWidget(parent)


class QtPushButton(QtWidgetWrapper):
    count = 0

    def create(self, parent):
        self.widget = QPushButton(parent)

    def bind(self):
        self.widget.clicked.connect(self.on_clicked)

    def on_clicked(self):
        self.count += 1
        def printer():
            print 'clicked'
        task = CallTask(lambda res: None, printer)
        self.post(task)
        if self.count > 5:
            self.post(None)

    def show(self):
        self.widget.show()


#------------------------------------------------------------------------------
# Toolkit Application
#------------------------------------------------------------------------------
class ToolkitApplication(object):

    def __init__(self):
        self._main_queue = Queue.PriorityQueue()
        self._ui_queue = Queue.PriorityQueue()
        self._gui_app = None
        self._gui_thread = threading.Thread(target=self._init_gui_app)
        self._gui_thread.daemon = True
        self._gui_thread.start()
        self._ui_queue.put((0, 'create_app'))

    def _init_gui_app(self):
        queue = self._ui_queue
        get = queue.get
        done = queue.task_done
        while True:
            priority, task = get()
            if task == 'create_app':
                self.create_ui_app()
                done()
            elif task == 'start_app':
                self._init_ui_loop()
                done()
                return
            else:
                task.execute()
                done()

    def post_to_main(self, task, priority=100):
        item = (priority, task)
        self._main_queue.put(item, False)

    def post_to_ui(self, task, priority=100):
        item = (priority, task)
        self._ui_queue.put(item, False)

    def mainloop(self):
        self._ui_queue.put((100, 'start_app'))
        self.run()

    def run(self):
        queue = self._main_queue
        get = queue.get
        done = queue.task_done
        while True:
            priority, task = get()
            if task is None:
                done()
                break
            try:
                task.execute()
            except Exception as e:
                print 'exception occurred on main thread'
                print e
            except:
                break
            finally:
                done()

    def _dispatch_ui_tasks(self):
        queue = self._ui_queue
        get = queue.get
        done = queue.task_done
        while True:
            priority, task = get()
            if task is None:
                done()
                break
            self.call_on_ui(self._handle_ui_task, task)
            done()

    def _handle_ui_task(self, task):
        try:
            task.execute()
        except Exception as e:
            print 'exception occurred in ui task handler'
            print e


    def _init_ui_loop(self):
        th = threading.Thread(target=self._dispatch_ui_tasks)
        th.daemon = True
        self._gui_thread = th
        self.call_on_ui(th.start)
        self.start_ui_loop()

    def call_on_ui(self, callback, *args, **kwargs):
        pass

    def create_ui_app(self):
        pass

    def start_ui_loop(self):
        pass


class QtApplication(ToolkitApplication):

    def call_on_ui(self, callback, *args, **kwargs):
        DeferredCaller.enqueue(callback, *args, **kwargs)

    def start_ui_loop(self):
        self._qapp.exec_()

    def create_ui_app(self):
        self._qapp = QApplication([])


class QtToolkit(object):

    def __init__(self, app):
        self.app = app


app = QtApplication()
tk = QtToolkit(app)

button = QtPushButton(None, tk)

task = CallTask(lambda res: None, button.create, None)
app.post_to_ui(task)

task = CallTask(lambda res: None, button.show)
app.post_to_ui(task)

app.mainloop()

