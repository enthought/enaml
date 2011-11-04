from .symbolics import ConstraintVariable


class BoxModel(object):
    """ Provide ConstraintVariables describing a box.

    """

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

class MarginBoxModel(BoxModel):
    """ Provide ConstraintVariables describing a box with margins.

    """

    __slots__ = ('margin_left', 'margin_right', 'margin_top', 'margin_bottom',
        'contents_left', 'contents_right', 'contents_width', 'contents_height',
        'contents_width', 'contents_top', 'contents_bottom',
        'contents_v_center', 'contents_h_center')

    def __init__(self):
        super(MarginBoxModel, self).__init__()
        for primitive in ('left', 'right', 'top', 'bottom'):
            attr = 'margin_%s' % primitive
            setattr(self, attr, ConstraintVariable('%s_%x' % (attr, id(self))))
        self.contents_left = self.left + self.margin_left
        self.contents_top = self.top + self.margin_top
        self.contents_right = self.right - self.margin_right
        self.contents_bottom = self.bottom - self.margin_bottom
        self.contents_width = self.contents_right - self.contents_left
        self.contents_height = self.contents_bottom - self.contents_top
        self.contents_v_center = self.contents_top + self.contents_height / 2.0
        self.contents_h_center = self.contents_left + self.contents_width / 2.0
