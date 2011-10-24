from .symbolics import ConstraintVariable


class BoxModel(object):

    __slots__ = ('left', 'right', 'width', 'height',
                 'top', 'bottom', 'v_center', 'h_center')

    def __init__(self):
        self.left = ConstraintVariable('left_%x' % id(self))
        self.top = ConstraintVariable('top_%x' % id(self))
        self.width = ConstraintVariable('width_%x' % id(self))
        self.height = ConstraintVariable('height_%x' % id(self))
        self.right = self.left + self.width
        self.bottom = self.top + self.height
        self.v_center = self.top + self.height / 2.0
        self.h_center = self.left + self.width / 2.0

