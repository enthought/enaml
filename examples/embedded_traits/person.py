#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.etsconfig.etsconfig import ETSConfig
from traits.api import HasTraits, Str, Range, Any, on_trait_change
from traitsui.api import View, Item, CustomEditor, Label

from enaml.stdlib.sessions import simple_app

if ETSConfig.toolkit == 'wx':
    from enaml.wx.wx_local_server import WxLocalServer as LocalServer
    from enaml.wx.wx_client_session import WxClientSession as ClientSession
else:
    from enaml.qt.qt_local_server import QtLocalServer as LocalServer
    from enaml.qt.qt_client_session import QtClientSession as ClientSession
    
#    from enaml.qt.q_single_widget_layout import QSingleWidgetLayout


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


def make_panel(parent):
    if ETSConfig.toolkit == 'wx':
        import wx
        from enaml.wx.wx_single_widget_sizer import wxSingleWidgetSizer
        panel = wx.Panel(parent)
        panel.SetSizer(wxSingleWidgetSizer())
    else:
        from enaml.qt.qt.QtGui import QFrame
        from enaml.qt.q_single_widget_layout import QSingleWidgetLayout
        panel = QFrame(parent.parentWidget())
        panel.setLayout(QSingleWidgetLayout())
    return panel

    
if __name__ == '__main__':
    import enaml
    with enaml.imports():
        from person_view import PersonView
    
    john = Person(first_name='John', last_name='Doe', age=42)
    app = simple_app('john', 'A view of the Person john', PersonView, 
       person=john) 
    server = LocalServer(app)
    client = server.local_client()

    def make_traitsui(session, proxy, parent):
        proxy.traitsui = john.edit_traits(kind='subpanel', parent=parent)
        control = proxy.traitsui.control
        if ETSConfig.toolkit != 'wx':
            control.setParent(parent) # XXX why isn't parent being set correctly?
        return control
    
    def session_factory(session_id, username, router, factories):
        session = ClientSession(session_id, username, router, factories)
        session._proxies['person'] = make_traitsui
        return session
        

    def enaml_factory(parent, editor, client, session_name, panel_name):
        print 'enaml', parent
        panel = make_panel(parent)
            
        def local_session_factory(session_id, username, router, factories):
            session = editor.value(session_id, username, router, factories)
            session._proxies[panel_name] = lambda *args: panel
            return session
        
        client.start_session(session_name, local_session_factory)
        return panel
    
    class TraitsEnamlView(HasTraits):
        
        session_factory = Any(ClientSession)
        
        view = View(
            Item('session_factory', editor=CustomEditor(factory=enaml_factory,
                    args=(client, 'john', 'panel')),
                show_label=False),
            resizable=True,
            width=200,
            height=200,
        )
    
    person_view = TraitsEnamlView(session_factory=session_factory)
    person_view.edit_traits()

    server.start()

