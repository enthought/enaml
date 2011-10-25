#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .style_trait import StyleTrait


#------------------------------------------------------------------------------
# Alignment
#------------------------------------------------------------------------------
class Alignment(int):

    __slots__ = ()

    DEFAULT = 0x0

    LEFT = 0x1

    RIGHT = 0x2

    HCENTER = 0x4

    JUSTIFY = 0x8

    BOTTOM = 0x10

    TOP = 0x20

    VCENTER = 0x40

    CENTER = VCENTER | HCENTER

    HORIZONTAL_MASK = LEFT | RIGHT | HCENTER | JUSTIFY

    VERTICAL_MASK = TOP | BOTTOM | VCENTER

    def __new__(cls, value=0):
        if not isinstance(value, int):
            raise TypeError('Alignment values must be integers.')
        return int.__new__(cls, value)

    def __repr__(self):
        parts = []
        if self == self.DEFAULT:
            parts.append('default')
        else:
            if self & self.LEFT:
                parts.append('left')
            elif self & self.RIGHT:
                parts.append('right')
            elif self & self.JUSTIFY:
                parts.append('justify')

            if self & self.BOTTOM:
                parts.append('bottom')
            elif self & self.TOP:
                parts.append('top')

            if self & self.HCENTER and self & self.VCENTER:
                parts.append('center')
            elif self & self.HCENTER:
                parts.append('hcenter')
            elif self & self.VCENTER:
                parts.append('vcenter')

        return 'Alignment(%s)' % ' | '.join(parts)

    def __str__(self):
        return self.__repr__()

    def default(self):
        return Alignment()

    def left(self):
        val = (self & ~self.HORIZONTAL_MASK) | self.LEFT
        return Alignment(val)

    def right(self):
        val = (self & ~self.HORIZONTAL_MASK) | self.RIGHT
        return Alignment(val)

    def hcenter(self):
        val = (self & ~self.HORIZONTAL_MASK) | self.HCENTER
        return Alignment(val)

    def justify(self):
        val = (self & ~self.HORIZONTAL_MASK) | self.JUSTIFY
        return Alignment(val)

    def top(self):
        val = (self & ~self.VERTICAL_MASK) | self.TOP
        return Alignment(val)

    def bottom(self):
        val = (self & ~self.VERTICAL_MASK) | self.BOTTOM
        return Alignment(val)

    def vcenter(self):
        val = (self & ~self.VERTICAL_MASK) | self.VCENTER
        return Alignment(val)

    def center(self):
        return Alignment(self.CENTER)



class AlignmentTrait(StyleTrait):

    def create_default(self, obj, name):
        return Alignment()

    def convert(self, obj, name, value):
        if isinstance(value, basestring):
            align = Alignment()
            vals = (val.lower() for val in value.strip().split())
            for val in vals:
                method = getattr(align, val, None)
                if method is not None:
                    align = method()
        else:
            try:
                align = Alignment(value)
            except TypeError:
                align = self.create_default(obj, name)
        return align


#------------------------------------------------------------------------------
# Margins
#------------------------------------------------------------------------------
class Margins(tuple):

    __slots__ = ()

    def __new__(cls, top=-1, right=-1, bottom=-1, left=-1):
        vals = (top, right, bottom, left)
        for idx, val in enumerate(vals):
            if not isinstance(val, int):
                raise TypeError('Margin values must be integers')
            if val < -1:
                name = ('top', 'right', 'bottom', 'left')[idx]
                msg = 'Invalid margin value: %s=%s' % (name, val)
                raise ValueError(msg)
        return tuple.__new__(cls, vals)

    def __repr__(self):
        templ = 'Margins(top=%s, right=%s, bottom=%s, left=%s)'
        return templ % self

    def __str__(self):
        return self.__repr__()

    def clone(self, top=None, right=None, bottom=None, left=None):
        these = (top, right, bottom, left)
        vals = ((this if this is not None else other)
                for (this, other) in zip(these, self))
        return Margins(*vals)

    @property
    def top(self):
        return self[0]

    @property
    def right(self):
        return self[1]

    @property
    def bottom(self):
        return self[2]

    @property
    def left(self):
        return self[3]


class MarginsTrait(StyleTrait):

    def create_default(self, obj, name):
        return Margins()

    def convert(self, obj, name, value):
        if isinstance(value, (tuple, list)):
            try:
                n = len(value)
                if n == 0:
                    margins = self.create_default(obj, name)
                elif n == 1:
                    v = value[0]
                    margins = Margins(v, v, v, v)
                elif n == 2:
                    v1, v2 = value
                    margins = Margins(v1, v2, v1, v2)
                elif n == 3:
                    v1, v2, v3 = value
                    margins = Margins(v1, v2, v3, v2)
                else:
                    v1, v2, v3, v4 = value[:4]
                    margins = Margins(v1, v2, v3, v4)
            except (ValueError, TypeError):
                margins = self.create_default(obj, name)
        else:
            try:
                margins = Margins(value, value, value, value)
            except (ValueError, TypeError):
                margins = self.create_default(obj, name)
        return margins


#------------------------------------------------------------------------------
# Size
#------------------------------------------------------------------------------
class Size(tuple):

    __slots__ = ()

    def __new__(cls, width=-1, height=-1):
        vals = (width, height)
        for idx, val in enumerate(vals):
            if not isinstance(val, int):
                raise TypeError('Size values must be integers')
            if val < -1:
                name = ('width', 'height')[idx]
                msg = 'Invalid size value: %s=%s' % (name, val)
                raise ValueError(msg)
        return tuple.__new__(cls, vals)

    def __repr__(self):
        templ = 'Size(width=%s, height=%s)'
        return templ % self

    def __str__(self):
        return self.__repr__()

    def clone(self, width=None, height=None):
        width = width if width is not None else self.width
        height = height if height is not None else self.height
        return Size(width, height)

    @property
    def width(self):
        return self[0]

    @property
    def height(self):
        return self[1]


class SizeTrait(StyleTrait):

    def create_default(self, obj, name):
        return Size()

    def convert(self, obj, name, value):
        if isinstance(value, (tuple, list)):
            try:
                n = len(value)
                if n == 0:
                    size = self.create_default(obj, name)
                elif n == 1:
                    v = value[0]
                    size = Size(v, v)
                else:
                    v1, v2 = value[:2]
                    size = Size(v1, v2)
            except (ValueError, TypeError):
                size = self.create_default(obj, name)
        else:
            try:
                size = Size(value, value)
            except (ValueError, TypeError):
                size = self.create_default(obj, name)
        return size


#------------------------------------------------------------------------------
# SizePolicy
#------------------------------------------------------------------------------
class SizePolicyFlag(int):

    __slots__ = ()

    DEFAULT = -1

    FIXED = 0

    MINIMUM = 1

    MAXIMUM = 2

    PREFERRED = 3

    EXPANDING = 4

    MINIMUM_EXPANDING = 5

    IGNORED = 6

    __allowed__ = frozenset((DEFAULT, FIXED, MINIMUM, MAXIMUM, PREFERRED,
                             EXPANDING, MINIMUM_EXPANDING, IGNORED))

    def __new__(cls, value=-1):
        if not isinstance(value, int):
            raise TypeError('Policy flag values must be integers')
        if value not in cls.__allowed__:
            raise ValueError('Invalid policy flag: `%s`' % value)
        return int.__new__(cls, value)

    def __repr__(self):
        if self == self.DEFAULT:
            inner = 'default'
        elif self == self.FIXED:
            inner = 'fixed'
        elif self == self.MINIMUM:
            inner = 'minimum'
        elif self == self.MAXIMUM:
            inner = 'maximum'
        elif self == self.PREFERRED:
            inner = 'preferred'
        elif self == self.EXPANDING:
            inner = 'expanding'
        else:
            inner = 'ignored'
        return 'SizePolicyFlag(%s)' % inner

    def __str__(self):
        return self.__repr__()

    def default(self):
        return SizePolicyFlag(self.DEFAULT)

    def fixed(self):
        return SizePolicyFlag(self.FIXED)

    def minimum(self):
        return SizePolicyFlag(self.MINIMUM)

    def maximum(self):
        return SizePolicyFlag(self.MAXIMUM)

    def preferred(self):
        return SizePolicyFlag(self.PREFERRED)

    def expanding(self):
        return SizePolicyFlag(self.EXPANDING)

    def minimum_expanding(self):
        return SizePolicyFlag(self.MINIMUM_EXPANDING)

    def ignored(self):
        return SizePolicyFlag(self.IGNORED)


class SizePolicy(tuple):

    __slots__ = ()

    def __new__(cls, horizontal=None, vertical=None):
        if horizontal is None and vertical is None:
            horizontal = vertical = SizePolicyFlag().default()
        elif vertical is None:
            horizontal = vertical = SizePolicyFlag(horizontal)
        elif horizontal is None:
            horizontal = vertical = SizePolicyFlag(vertical)
        else:
            horizontal = SizePolicyFlag(horizontal)
            vertical = SizePolicyFlag(vertical)
        return tuple.__new__(cls, (horizontal, vertical))

    def __repr__(self):
        return 'SizePolicy(%s, %s)' % (self[0], self[1])

    def __str__(self):
        return self.__repr__()

    def clone(self, horizontal=None, vertical=None):
        horizontal = horizontal if horizontal is not None else self.horizontal
        vertical = vertical if vertical is not None else self.vertical
        return SizePolicy(horizontal, vertical)

    @property
    def horizontal(self):
        return self[0]

    @property
    def vertical(self):
        return self[1]


class SizePolicyTrait(StyleTrait):

    def create_default(self, obj, name):
        return SizePolicy()

    def convert(self, obj, name, value):

        def get_flag(val):
            if isinstance(val, basestring):
                val = val.lower()
                flag = SizePolicyFlag()
                method = getattr(flag, val, None)
                if method is not None:
                    flag = method()
            else:
                flag = SizePolicyFlag(val)
            return flag

        if isinstance(value, (tuple, list)):
            try:
                n = len(value)
                if n == 0:
                    policy = self.create_default(obj, name)
                elif n == 1:
                    flag = get_flag(value[0])
                    policy = SizePolicy(flag)
                else:
                    hflag = get_flag(value[0])
                    vflag = get_flag(value[1])
                    policy = SizePolicy(hflag, vflag)
            except (ValueError, TypeError):
                policy = self.create_default(obj, name)
        else:
            try:
                flag = get_flag(value)
                policy = SizePolicy(flag)
            except (ValueError, TypeError):
                policy = self.create_default(obj, name)

        return policy


#------------------------------------------------------------------------------
# Spacing
#------------------------------------------------------------------------------
class SpacingTrait(StyleTrait):

     def create_default(self, obj, name):
        return -1

     def convert(self, obj, name, value):
         if not isinstance(value, int) or value < -1:
             spacing = self.create_default(obj, name)
         else:
             spacing = value
         return spacing

#------------------------------------------------------------------------------
# Stretch
#------------------------------------------------------------------------------
class StretchTrait(StyleTrait):

     def create_default(self, obj, name):
        return -1

     def convert(self, obj, name, value):
         if not isinstance(value, int) or value < -1:
             spacing = self.create_default(obj, name)
         else:
             spacing = value
         return spacing



