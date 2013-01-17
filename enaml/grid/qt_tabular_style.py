#------------------------------------------------------------------------------
#  Copyright (c) 2013, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
# XXX needs documentation
from enaml.colors import parse_color
from enaml.layout.geometry import Box
from enaml.qt.qt.QtCore import Qt
from enaml.qt.qt.QtGui import QFont, QColor, QPen


FONT_WEIGHT = {
    'light': QFont.Light,
    'normal': QFont.Normal,
    'bold': QFont.Bold,
}


FONT_STYLE = {
    'normal': QFont.StyleNormal,
    'italic': QFont.StyleItalic,
    'oblique': QFont.StyleOblique,
}


BORDER_STYLE = {
    'solid': Qt.SolidLine,
    'dotted': Qt.DotLine,
    'dashed': Qt.DashLine,
}


ALIGN = {
    'left': Qt.AlignLeft,
    'right': Qt.AlignRight,
    'center': Qt.AlignHCenter,
}


VERTICAL_ALIGN = {
    'top': Qt.AlignTop,
    'bottom': Qt.AlignBottom,
    'center': Qt.AlignVCenter,
}


class QtCellBorder(object):

    __slots__ = ('left', 'top', 'right', 'bottom')

    def __init__(self):
        self.left = None
        self.top = None
        self.right = None
        self.bottom = None


def make_border_pen(border):
    pen = QPen()
    if 'color' in border:
        color = parse_color(border['color'])
        if color is not None:
            pen.setBrush(QColor.fromRgbF(*color))
    if 'width' in border:
        pen.setWidth(border['width'])
    if 'style' in border:
        pen.setStyle(BORDER_STYLE.get(border['style'], Qt.SolidLine))
    return pen


class QtTabularStyle(object):

    __slots__ = (
        'background', 'foreground', 'align', 'margin', 'border', 'padding',
        'format', 'font',
    )

    def __init__(self):
        self.background = None
        self.foreground = None
        self.align = None
        self.margin = None
        self.border = None
        self.padding = None
        self.format = None
        self.font = None

    @classmethod
    def init_from(cls, style):

        self = cls()

        if 'background' in style:
            background = parse_color(style['background'])
            if background is not None:
                self.background = QColor.fromRgbF(*background)

        if 'foreground' in style:
            foreground = parse_color(style['foreground'])
            if foreground is not None:
                self.foreground = QColor.fromRgbF(*foreground)

        if 'font' in style:
            font = style['font']
            if '__q_font' in font:
                self.font = font['__q_font']
            else:
                q_font = QFont()
                if 'family' in font:
                    q_font.setFamily(font['family'])
                if 'weight' in font:
                    q_font.setWeight(FONT_WEIGHT.get(font['weight'], QFont.Normal))
                if 'style' in font:
                    q_font.setStyle(FONT_STYLE.get(font['style'], QFont.StyleNormal))
                if 'size' in font:
                    q_font.setPointSize(font['size'])
                self.font = q_font

        h_align = ALIGN.get(style.get('align'), Qt.AlignHCenter)
        v_align = VERTICAL_ALIGN.get(style.get('vertical_align'), Qt.AlignVCenter)
        self.align = h_align | v_align

        if 'margin' in style:
            m = Box(style['margin'])
            self.margin = (m.left, m.top, -m.right, -m.bottom)

        if 'padding' in style:
            p = Box(style['padding'])
            self.padding = (p.left, p.top, -p.right, -p.bottom)

        q_border = None
        if 'border' in style:
            if q_border is None:
                q_border = QtCellBorder()
            border = style['border']
            if '__q_border_pen' in border:
                pen = border['__q_border_pen']
            else:
                pen = border['__q_border_pen'] = make_border_pen(border)
            q_border.left = pen
            q_border.top = pen
            q_border.right = pen
            q_border.bottom = pen
        if 'left_border' in style:
            if q_border is None:
                q_border = QtCellBorder()
            border = style['left_border']
            if '__q_border_pen' in border:
                pen = border['__q_border_pen']
            else:
                pen = border['__q_border_pen'] = make_border_pen(border)
            q_border.left = pen
        if 'top_border' in style:
            if q_border is None:
                q_border = QtCellBorder()
            border = style['top_border']
            if '__q_border_pen' in border:
                pen = border['__q_border_pen']
            else:
                pen = border['__q_border_pen'] = make_border_pen(border)
            q_border.top = pen
        if 'right_border' in style:
            if q_border is None:
                q_border = QtCellBorder()
            border = style['right_border']
            if '__q_border_pen' in border:
                pen = border['__q_border_pen']
            else:
                pen = border['__q_border_pen'] = make_border_pen(border)
            q_border.right = pen
        if 'bottom_border' in style:
            if q_border is None:
                q_border = QtCellBorder()
            border = style['bottom_border']
            if '__q_border_pen' in border:
                pen = border['__q_border_pen']
            else:
                pen = border['__q_border_pen'] = make_border_pen(border)
            q_border.bottom = pen

        self.border = q_border

        return self

