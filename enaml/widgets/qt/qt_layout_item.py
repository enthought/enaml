from traits.api import HasTraits, implements

from ...layout.layout_item import ILayoutItemImpl


class QtLayoutItem(HasTraits):
    """ A mixin class for Qt components that implements the proper
    methods for a layout item.

    """
    implements(ILayoutItemImpl)
    
    def size(self):
        return (self.widget.width(), self.widget.height())
    
    def resize(self, width, height):
        self.resize(width, height)
    
    def pos(self):
        return (self.widget.x(), self.widget.y())
            
    def move(self, x, y):
        self.widget.move(x, y)
    
    def geometry(self):
        x, y = self.pos()
        w, h = self.size()
        return (x, y, w, h)
            
    def set_geometry(self, x, y, width, height):
        self.widget.setGeometry(x, y, width, height)

    def size_hint(self):
        size_hint = self.widget.sizeHint()
        return (size_hint.width(), size_hint.height())

