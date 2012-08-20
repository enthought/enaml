from enaml.widgets import *
from enaml.application import Application
from enaml.qt.qt_local_server import QtLocalServer
from enaml.stdlib.sessions import view_factory


@view_factory('main')
def create_view():
   main_window = MainWindow()

   # We can provided parents as we go, the parent-child relationship
   # is established automatically.
   dock_pane = DockPane(main_window)
   dock_container = Container(dock_pane)
   button1 = PushButton(dock_container, text='Button1')
   button2 = PushButton(dock_container, text='Button2')
   field1 = Field(dock_container, placeholder='Data...')

   # But, parents don't need to be provided immediately
   main_container = Container()
   html = Html(source='<h1><center>Hello World</center></h1>')

   # Things can be parented at any time, and the parent-child 
   # relationship will be made properly. Things just need to 
   # be parents "at some point"
   main_container.parent = main_window
   html.parent = main_container

   menu_bar = MenuBar(main_window)
   file_menu = Menu(menu_bar, title='File')
   action1 = Action(file_menu, text='New')
   action2 = Action(file_menu, text='Open')
   edit_menu = Menu(menu_bar, title='Edit')
   action3 = Action(edit_menu, text='Cut')
   action4 = Action(edit_menu, text='Copy')
   action5 = Action(edit_menu, text='Past', enabled=False)
   
   return main_window


if __name__ == '__main__':
    app = Application([create_view()])
    server = QtLocalServer(app)
    client = server.local_client()
    client.start_session('main')
    server.start()

