#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from ..layout_item import AbstractTkLayoutItem


class QtLayoutItem(AbstractTkLayoutItem):
    """ A mixin class for Qt components that implements the proper
    methods for a layout item.

    """
    def size(self):
        return (self.widget.width(), self.widget.height())
    
    def resize(self, width, height):
        self.widget.resize(width, height)
    
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

