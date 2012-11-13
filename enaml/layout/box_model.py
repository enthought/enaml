#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .constraint_variable import ConstraintVariable


class BoxModel(object):
    """ A class which provides a simple constraints box model.

    Primitive Variables:
        left, top, width, height

    Derived Variables:
        right, bottom, v_center, h_center

    """
    __slots__ = (
        'left', 'top', 'width', 'height', 'right', 'bottom', 'v_center',
        'h_center'
    )

    def __init__(self, owner):
        """ Initialize a BoxModel.

        Parameters
        ----------
        owner : str
            A string which uniquely identifies the owner of this box
            model.

        """
        self.left = ConstraintVariable('left', owner)
        self.top = ConstraintVariable('top', owner)
        self.width = ConstraintVariable('width', owner)
        self.height = ConstraintVariable('height', owner)
        self.right = self.left + self.width
        self.bottom = self.top + self.height
        self.v_center = self.top + self.height / 2.0
        self.h_center = self.left + self.width / 2.0


class ContentsBoxModel(BoxModel):
    """ A BoxModel subclass which adds an inner contents box.

    Primitive Variables:
        contents_[left|right|top|bottom]

    Derived Variables:
        contents_[width|height|v_center|h_center]

    """
    __slots__ = (
        'contents_left', 'contents_right', 'contents_top', 'contents_bottom',
        'contents_width', 'contents_height', 'contents_v_center',
        'contents_h_center'
    )

    def __init__(self, owner):
        """ Initialize a ContainerBoxModel.

        Parameters
        ----------
        owner : string
            A string which uniquely identifies the owner of this box
            model.

        """
        super(ContentsBoxModel, self).__init__(owner)
        self.contents_left = ConstraintVariable('contents_left', owner)
        self.contents_right = ConstraintVariable('contents_right', owner)
        self.contents_top = ConstraintVariable('contents_top', owner)
        self.contents_bottom = ConstraintVariable('contents_bottom', owner)
        self.contents_width = self.contents_right - self.contents_left
        self.contents_height = self.contents_bottom - self.contents_top
        self.contents_v_center = self.contents_top + self.contents_height / 2.0
        self.contents_h_center = self.contents_left + self.contents_width / 2.0

