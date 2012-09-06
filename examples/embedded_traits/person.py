#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import HasTraits, Str, Range, on_trait_change

from enaml.stdlib.sessions import simple_app
from enaml.qt.qt_local_server import QtLocalServer
from enaml.qt.qt_client_session import QtClientSession
#from enaml.qt.qt_window import QWindowLayout
from enaml.qt.q_single_widget_layout import QSingleWidgetLayout


class Person(HasTraits):
    """ A simple class representing a person object.

    """
    last_name = Str

    first_name = Str

    age = Range(low=0)

    @on_trait_change('age')
    def debug_print(self):
        """ Prints out a debug message whenever the person's age changes.

        """
        templ = "{first} {last} is {age} years old."
        print templ.format(first=self.first_name, 
                           last=self.last_name, 
                           age=self.age)



if __name__ == '__main__':
    import enaml
    with enaml.imports():
        from person_view import PersonView
    
    john = Person(first_name='John', last_name='Doe', age=42)
    app = simple_app('john', 'A view of the Person john', PersonView, 
       person=john) 

    from PySide.QtGui import QApplication, QMainWindow, QFrame
    qapp = QApplication.instance() or QApplication([])
    panel = QFrame()
    panel.setLayout(QSingleWidgetLayout())
    panel.show()

    def make_traitsui(session, proxy, parent):
        proxy.traitsui = john.edit_traits(kind='subpanel', parent=parent)
        control = proxy.traitsui.control
        control.setParent(parent) # XXX why isn't parent being set correctly?
        return control

    def make_panel(session, proxy, parent):
        return panel

    def local_session_factory(session_id, username, router, factories):
        session = QtClientSession(session_id, username, router, factories)
        session._proxies['person'] = make_traitsui
        session._proxies['panel'] = make_panel
        return session


    server = QtLocalServer(app)
    client = server.local_client()
    client.start_session('john', local_session_factory)
    server.start()

