#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from casuarius import ConstraintVariable


class BoxModel(object):
    """ Provides ConstraintVariables describing a box with margins.

    Primitive Variables:
        - left
        - top
        - width
        - height
    
    Derived Variables:
        - right
        - bottom
        - v_center
        - h_center

    """
    def __init__(self, component):
        label = '{0}_{1:x}'.format(type(component).__name__, id(component))
        for primitive in ('left', 'top', 'width', 'height'):
            var = ConstraintVariable('{0}_{1}'.format(primitive, label))
            setattr(self, primitive, var) 
        self.right = self.left + self.width
        self.bottom = self.top + self.height
        self.v_center = self.top + self.height / 2.0
        self.h_center = self.left + self.width / 2.0        


class MarginBoxModel(BoxModel):
    """ Provides ConstraintVariables describing a box with margins.

    Primitive Variables:
        - margin_[left|right|top|bottom]
    
    Derived Variables:
        - contents_[left|top|right|bottom|width|height|v_center|h_center]
    
    """
    def __init__(self, component):
        super(MarginBoxModel, self).__init__(component)
        label = '{0}_{1:x}'.format(type(component).__name__, id(component))
        for primitive in ('left', 'right', 'top', 'bottom'):
           attr = 'margin_{0}'.format(primitive)
           var = ConstraintVariable('{0}_{1}'.format(attr, label))
           setattr(self, attr, var)
        self.contents_left = self.left + self.margin_left
        self.contents_top = self.top + self.margin_top
        self.contents_right = self.right - self.margin_right
        self.contents_bottom = self.bottom - self.margin_bottom
        self.contents_width = self.contents_right - self.contents_left
        self.contents_height = self.contents_bottom - self.contents_top
        self.contents_v_center = self.contents_top + self.contents_height / 2.0
        self.contents_h_center = self.contents_left + self.contents_width / 2.0

