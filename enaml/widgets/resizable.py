#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from abc import ABCMeta, abstractmethod

from traits.api import HasTraits


class AbstractTkResizable(object):
    """ The abstract toolkit Resizable interface.

    """
    __metaclass__ = ABCMeta
    
    @abstractmethod
    def size(self):
        """ Returns the size of the internal toolkit widget, ignoring any
        windowing decorations, as a (width, height) tuple of integers.

        """
        raise NotImplementedError
    
    @abstractmethod
    def size_hint(self):
        """ Returns a (width, height) tuple of integers which represent
        the suggested size of the widget for its current state, ignoring
        any windowing decorations. This value is used by the layout 
        manager to determine how much space to allocate the widget.

        """
        raise NotImplementedError

    @abstractmethod
    def resize(self, width, height):
        """ Resizes the internal toolkit widget according the given
        width and height integers, ignoring any windowing decorations.

        """
        raise NotImplementedError
    
    @abstractmethod
    def min_size(self):
        """ Returns the hard minimum (width, height) of the widget, 
        ignoring any windowing decorations. A widget will not be able
        to be resized smaller than this value

        """
        raise NotImplementedError

    @abstractmethod
    def set_min_size(self, min_width, min_height):
        """ Set the hard minimum width and height of the widget, ignoring
        any windowing decorations. A widget will not be able to be resized 
        smaller than this value.

        """
        raise NotImplementedError

    @abstractmethod
    def pos(self):
        """ Returns the position of the internal toolkit widget as an
        (x, y) tuple of integers, including any windowing decorations. 
        The coordinates should be relative to the origin of the widget's 
        parent, or to the screen if the widget is toplevel.

        """
        raise NotImplementedError
    
    @abstractmethod
    def move(self, x, y):
        """ Moves the internal toolkit widget according to the given
        x and y integers which are relative to the origin of the
        widget's parent and includes any windowing decorations.

        """
        raise NotImplementedError
        
    @abstractmethod
    def frame_geometry(self):
        """ Returns an (x, y, width, height) tuple of geometry info
        for the internal toolkit widget, including any windowing
        decorations.

        """
        raise NotImplementedError

    @abstractmethod
    def geometry(self):
        """ Returns an (x, y, width, height) tuple of geometry info
        for the internal toolkit widget, ignoring any windowing
        decorations.

        """
        raise NotImplementedError
    
    @abstractmethod
    def set_geometry(self, x, y, width, height):
        """ Sets the geometry of the internal widget to the given
        x, y, width, and height values, ignoring any windowing 
        decorations.

        """
        raise NotImplementedError
        

class Resizable(HasTraits):
    """ A mixin class which declares the resizable interface for an
    Enaml component. The Component class should be in inheritence 
    heierarchy when the class is used as a mixin.

    """
    def size(self):
        """ Returns the size tuple as given by the abstract widget.

        """
        return self.abstract_obj.size()
    
    def size_hint(self):
        """ Returns the size hint tuple as given by the abstract widget
        for its current state.

        """
        return self.abstract_obj.size_hint()

    def resize(self, width, height):
        """ Resize the abstract widget as specified by the given
        width and height integers.

        """
        self.abstract_obj.resize(width, height)
    
    def min_size(self):
        """ Returns the hard minimum (width, height) of the widget, 
        ignoring any windowing decorations. A widget will not be able
        to be resized smaller than this value

        """
        return self.abstract_obj.min_size()

    def set_min_size(self, min_width, min_height):
        """ Set the hard minimum width and height of the widget. A widget
        should not be able to be resized smaller than this value.

        """
        self.abstract_obj.set_min_size(min_width, min_height)

    def pos(self):
        """ Returns the position tuple as given by the abstract widget.

        """
        return self.abstract_obj.pos()
    
    def move(self, x, y):
        """ Moves the abstract widget to the given x and y integer
        coordinates which are given relative to the parent origin.

        """
        self.abstract_obj.move(x, y)
    
    def geometry(self):
        """ Returns the (x, y, width, height) geometry tuple as given
        by the abstract widget.

        """
        return self.abstract_obj.geometry()
    
    def set_geometry(self, x, y, width, height):
        """ Sets the geometry of the abstract widget with the given
        integer values.

        """
        self.abstract_obj.set_geometry(x, y, width, height)

