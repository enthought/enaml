#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from abc import ABCMeta, abstractmethod
from traits.api import HasTraits, Instance, Property, List

from ..layout.box_model import BoxModel
from ..layout.symbolics import LinearConstraint


class AbstractTkLayoutItem(object):

    __metaclass__ = ABCMeta

    @abstractmethod
    def size(self):
        raise NotImplementedError
    
    @abstractmethod
    def resize(self, width, height):
        raise NotImplementedError
    
    @abstractmethod
    def pos(self):
        raise NotImplementedError
    
    @abstractmethod
    def move(self, x, y):
        raise NotImplementedError
    
    @abstractmethod
    def geometry(self):
        raise NotImplementedError
    
    @abstractmethod
    def set_geometry(self, x, y, width, height):
        raise NotImplementedError

    @abstractmethod
    def size_hint(self):
        raise NotImplementedError


class LayoutItem(HasTraits):
    """ A mixin class for Enaml components which adds a box model,
    constraints, and layout methods necessary for a layout manager
    to do its job.

    """
    _box_model = Instance(BoxModel, ())

    constraints = List(Instance(LinearConstraint))

    left = Property

    top = Property

    width = Property

    height = Property

    right = Property

    bottom = Property

    v_center = Property

    h_center = Property

    def _get_left(self):
        return self._box_model.left
    
    def _get_top(self):
        return self._box_model.top
    
    def _get_width(self):
        return self._box_model.width
    
    def _get_height(self):
        return self._box_model.height
    
    def _get_right(self):
        return self._box_model.right
    
    def _get_bottom(self):
        return self._box_model.bottom
    
    def _get_v_center(self):
        return self._box_model.v_center
    
    def _get_h_center(self):
        return self._box_model.h_center
    
    def size(self):
        return self.abstract_widget.size()
    
    def resize(self, width, height):
        self.abstract_widget.resize(width, height)
    
    def pos(self):
        return self.abstract_widget.pos()
    
    def move(self, x, y):
        self.abstract_widget.move(x, y)
    
    def geometry(self):
        return self.abstract_widget.geometry()
    
    def set_geometry(self, x, y, width, height):
        self.abstract_widget.set_geometry(x, y, width, height)

    def size_hint(self):
        return self.abstract_widget.size_hint()

