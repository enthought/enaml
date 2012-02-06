#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from casuarius import ConstraintVariable


class BoxModel(object):
    """ Provide ConstraintVariables describing a box.

    """
    def __init__(self, component):
        label = '{0}_{1:x}'.format(type(component).__name__, id(component))
        self.left = ConstraintVariable('left_{0}'.format(label))
        self.top = ConstraintVariable('top_{0}'.format(label))
        self.width = ConstraintVariable('width_{0}'.format(label))
        self.height = ConstraintVariable('height_{0}'.format(label))
        self.right = self.left + self.width
        self.bottom = self.top + self.height
        self.v_center = self.top + self.height / 2.0
        self.h_center = self.left + self.width / 2.0


class MarginBoxModel(BoxModel):
    """ Provide ConstraintVariables describing a box with margins.

    """
    def __init__(self, component):
        super(MarginBoxModel, self).__init__(component)
        label = '{0}_{1:x}'.format(type(component).__name__, id(component))
        for primitive in ('left', 'right', 'top', 'bottom'):
            attr = 'margin_{0}'.format(primitive)
            setattr(self, attr, ConstraintVariable('{0}_{1}'.format(attr, label)))
        self.contents_left = self.left + self.margin_left
        self.contents_top = self.top + self.margin_top
        self.contents_right = self.right - self.margin_right
        self.contents_bottom = self.bottom - self.margin_bottom
        self.contents_width = self.contents_right - self.contents_left
        self.contents_height = self.contents_bottom - self.contents_top
        self.contents_v_center = self.contents_top + self.contents_height / 2.0
        self.contents_h_center = self.contents_left + self.contents_width / 2.0

