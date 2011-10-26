from .symbolics import ConstraintVariable


class BoxModel(object):

    __slots__ = ('left', 'right', 'width', 'height',
                 'top', 'bottom', 'v_center', 'h_center')

    def __init__(self):
        self.left = ConstraintVariable('left')
        self.top = ConstraintVariable('top')
        self.width = ConstraintVariable('width')
        self.height = ConstraintVariable('height')
        self.right = self.left + self.width
        self.bottom = self.top + self.height
        self.v_center = self.top + self.height / 2.0
        self.h_center = self.left + self.width / 2.0

