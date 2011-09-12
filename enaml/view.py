from traits.api import HasStrictTraits, Instance

from .toolkit import Toolkit
from .util.style_sheet import StyleSheet
from .widgets.window import Window

  
class NamespaceProxy(object):
    """ A simple proxy object that converts a namespace dictionary
    into an object with attribute-like access.

    """
    def __init__(self, ns):
        self.__dict__ = ns
      

class View(HasStrictTraits):
    """ The View object provides a simple shell around an Enaml ui tree.

    Attributes
    ----------
    window : Instance(Window)
        The top-level Enaml window object for the view.

    ns : Instance(NamespaceProxy)
        A proxy into the global namespace of the enaml view.

    toolkit : Instance(Toolkit)
        The toolkit instance that was used to create the view.
    
    Methods
    -------
    show()
        Show the ui on the screen.

    hide()
        Hide the ui from the screen.

    """
    window = Instance(Window)

    ns = Instance(NamespaceProxy)

    toolkit = Instance(Toolkit)

    style_sheet = Instance(StyleSheet)

    def show(self):
        self.window.style_sheet = self.style_sheet
        self.window.show()
        self.toolkit.start_event_loop()
        
    def hide(self):
        self.window.hide()

    def set_style_sheet(self, style_sheet):
        self.style_sheet = style_sheet

    def _style_sheet_default(self):
        return self.toolkit.default_style_sheet()

