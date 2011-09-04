from traits.api import HasStrictTraits, Instance

from .widgets.window import Window

  
class NamespaceProxy(object):
    
    def __init__(self, ns):
        self.__dict__ = ns
      

class View(HasStrictTraits):
    
    window = Instance(Window)

    ns = Instance(NamespaceProxy)

    def show(self):
        self.window.show()
    
    def hide(self):
        self.window.hide()

