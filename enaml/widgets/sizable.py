#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from abc import ABCMeta, abstractmethod

from traits.api import HasTraits


class AbstractTkSizable(object):
    """ The abstract toolkit Sizable interface.

    """
    __metaclass__ = ABCMeta
    
    @abstractmethod
    def size_hint(self):
        """ Returns a (width, height) tuple of integers which represent
        the suggested size of the widget for its current state, for the
        purposes of layout computation. This value may be different than
        the size reported by geometry() if the widget's effective layout
        rect is different from its paintable rect.

        """
        raise NotImplementedError

    @abstractmethod
    def layout_geometry(self):
        """ Returns the (x, y, width, height) to of layout geometry
        info for the internal toolkit widget. This should ignore any
        windowing decorations, and may be different than the value
        returned by geometry() if the widget's effective layout rect
        is different from its paintable rect.

        """
        raise NotImplementedError

    @abstractmethod
    def set_layout_geometry(self, x, y, width, height):
        """ Sets the layout geometry of the internal widget to the 
        given x, y, width, and height values. The parameters passed
        are equivalent semantics to layout_geometry().

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

    @abstractmethod
    def min_size(self):
        """ Returns the hard minimum (width, height) of the widget, 
        ignoring any windowing decorations. A window will not be able
        to be resized smaller than this value

        """
        raise NotImplementedError

    @abstractmethod
    def set_min_size(self, min_width, min_height):
        """ Set the hard minimum width and height of the widget, ignoring
        any windowing decorations. A window will not be able to be resized 
        smaller than this value.

        """
        raise NotImplementedError

    @abstractmethod
    def max_size(self):
        """ Returns the hard maximum (width, height) of the widget, 
        ignoring any windowing decorations. A widget will not be able
        to be resized larger than this value

        """
        raise NotImplementedError

    @abstractmethod
    def set_max_size(self, max_width, max_height):
        """ Set the hard maximum width and height of the widget, ignoring
        any windowing decorations. A widget will not be able to be resized 
        larger than this value.

        """
        raise NotImplementedError


class Sizable(HasTraits):
    """ A mixin class which declares the sizable interface for an
    Enaml component. The Component class should be in inheritence 
    heierarchy when the class is used as a mixin.

    """
    def size_hint(self):
        """ Returns the size hint tuple as given by the abstract widget
        for its current state.

        """
        return self.abstract_obj.size_hint()

    def layout_geometry(self):
        """ Returns the (x, y, width, height) to of layout geometry
        info as given by the abstract object. It may be different from
        the value returned by geometry() if the widget's effective 
        layout rect is different from its paintable rect.

        """
        return self.abstract_obj.layout_geometry()

    def set_layout_geometry(self, x, y, width, height):
        """ Sets the layout geometry of the internal widget to the 
        given x, y, width, and height values. The parameters passed
        are equivalent semantics to layout_geometry().

        """
        self.abstract_obj.set_layout_geometry(x, y, width, height)

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

    def min_size(self):
        """ Returns the hard minimum (width, height) of the widget, 
        ignoring any windowing decorations. A window will not be able
        to be resized smaller than this value

        """
        return self.abstract_obj.min_size()

    def set_min_size(self, min_width, min_height):
        """ Set the hard minimum width and height of the widget, ignoring
        any windowing decorations. A window will not be able to be resized 
        smaller than this value.

        """
        self.abstract_obj.set_min_size(min_width, min_height)

    def max_size(self):
        """ Returns the hard maximum (width, height) of the widget, 
        ignoring any windowing decorations. A widget will not be able
        to be resized larger than this value

        """
        return self.abstract_obj.max_size()

    def set_max_size(self, max_width, max_height):
        """ Set the hard maximum width and height of the widget, ignoring
        any windowing decorations. A widget will not be able to be resized 
        larger than this value.

        """
        self.abstract_obj.set_max_size(max_width, max_height)

    def size(self):
        """ Returns the size tuple as given by the abstract widget.

        """
        _, _, width, height = self.geometry()
        return (width, height)

    def resize(self, width, height):
        """ Resize the abstract widget as specified by the given
        width and height integers.

        """
        x, y, _, _ = self.geometry()
        self.set_geometry(x, y, width, height)
        
    def pos(self):
        """ Returns the position tuple as given by the abstract widget.

        """
        x, y, _, _ = self.geometry()
        return (x, y)
    
    def move(self, x, y):
        """ Moves the abstract widget to the given x and y integer
        coordinates which are given relative to the parent origin.

        """
        _, _, width, height = self.geometry()
        self.set_geometry(x, y, width, height)

