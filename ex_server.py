#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from enaml.messaging.registry import register
from enaml.messaging.hub import message_hub

from enaml.qt.qt_local_application import QtLocalApplication
from enaml.backends.qt.qt_application import DeferredCaller


class QtLocalRemoteApplication(QtLocalApplication):

    def __init__(self, *args, **kwargs):
        super(QtLocalRemoteApplication, self).__init__(*args, **kwargs)
        def app_id():
            yield 'app'
        register(self, app_id())

    def receive(self, message):
        payload = message['payload']
        if payload['action'] == 'create':
            view_name = payload['name']
            view = self._views[view_name]
            tree = view.creation_tree()
            message = {
                'type': 'message',
                'target_id': 'app',
                'operation_id': message['operation_id'],
                'payload': {
                    'action': 'create',
                    'tree': tree,
                }
            } 
            message_hub.post_message(message)


if __name__ == '__main__':
    import enaml
    
    from enaml.zmq.zmq_server_worker import ZMQServerWorker

    with enaml.imports():
        from ex_server_view import MainView

    view = MainView()
    
    app = QtLocalRemoteApplication()
    app.serve('main', view)
    
    worker = ZMQServerWorker('tcp://127.0.0.1', '6000', '6001', DeferredCaller.enqueue)
    worker.daemon = True
    worker.start()

    app.mainloop()
    worker.stop()

