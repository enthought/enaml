#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from textwrap import dedent

from .style_trait import StyleTrait


_weight_map = {
    'light': 25,
    'normal': 50,
    'demi_bold': 63,
    'bold': 75,
    'black': 87,
}


_stretch_map = {
    'ultra_condensed': 50,
    'extra_condensed': 62,
    'condensed': 75,
    'semi_condensed': 87,
    'unstretched': 100,
    'semi_expanded': 112,
    'expanded': 125,
    'extra_expanded': 150,
    'ultra_expanded': 200,
}


_spacing_set = frozenset((
    'percentage',
    'absolute',
))


_style_set = frozenset((
    'normal',
    'italic',
    'oblique',
))


_family_hint_set = frozenset((
    'any',
    'sans_serif',
    'helvetica',
    'serif',
    'times',
    'type_writer',
    'courier',
    'old_english',
    'decorative',
    'monospace',
    'fantasy',
    'cursive',
    'system',
))


class Font(tuple):
    """ A tuple subclass which represents a font.

    """
    __slots__ = ()

    #: A default font instance that will be set at the end of the
    #: definition of this class. It is useful for comparison.
    default_font = None

    @classmethod
    def from_string(cls, font_string):
        """ Convert a space separated string into a font object.

        The schema for the string is as follows:

        family [point_size | weight | style | family_hint | *options]
            
        The family must appear first, but the remaining items can 
        appear in any order and can be any in quantity. Valid values 
        for the items are shown below. All values are case insenstive. 
        Invalid values are ignored. Duplicate items and items of the
        same class override any previous items of that class.
            
        family : a string
        
        point_size : an integer
        
        weight : one of ['light', 'normal', 'demi_bold', 'bold', 'black']
        
        style : one of ['italic', 'oblique']

        family_hint : one of ['sans_serif', 'helvetica', 'serif', 'times', 
                              'type_writer', 'courier', 'old_english', 
                              'decorative', 'monospace', 'fantasy', 
                              'cursive', 'system']
        
        *options : one or more of ['underline', 'strikethrough']

        Examples
        --------
        'consolas 12 bold'
        'times underline'
        'menlo italic 18 underline demi_bold'
        'inconsolata 14 black italic strikethrough monospace underline'

        """
        parts = [part.lower() for part in font_string.strip().split()]
        if not parts:
            raise ValueError('Invalid font string `%s`' % font_string)
    
        kw = {}
        kw['family'] = parts[0]

        for part in parts[1:]:
            
            try:
                point_size = int(part)
            except ValueError:
                pass
            else:
                kw['point_size'] = point_size
                continue
            
            # 'normal' is used for both weight and style. It's the
            # default for both, so we just skip it since we can't
            # resolve the ambiguity (nor do we need to).
            if part == 'normal':
                continue

            if part in _weight_map:
                kw['weight'] = part
            elif part in _style_set:
                kw['style'] = part
            elif part in _family_hint_set:
                kw['family_hint'] = part
            elif part == 'underline':
                kw['underline'] = True
            elif part == 'strikethrough':
                kw['strikethrough'] = True

        return Font(**kw)

    def __new__(cls, family='', point_size=-1, weight=-1, style='normal', 
        underline=False, strikethrough=False, family_hint='any', 
        spacing_type='percentage', letter_spacing=100.0, word_spacing=0.0, 
        stretch=100):
         
        #----------------------------------------------------------------------
        # Argument Type Checking
        #----------------------------------------------------------------------
        if not isinstance(family, basestring):
            raise TypeError('family must be a string')

        if not isinstance(point_size, int):
            raise TypeError('point_size must be an int')

        if not isinstance(weight, (int, basestring)):
            raise TypeError('weight must be an int or a string')

        if not isinstance(style, basestring):
            raise TypeError('style must be a string')

        if not isinstance(underline, bool):
            raise TypeError('underline must be a bool')

        if not isinstance(strikethrough, bool):
            raise TypeError('strikethrough must be a bool')

        if not isinstance(family_hint, basestring):
            raise TypeError('family_hint must be a string')

        if not isinstance(spacing_type, basestring):
            raise TypeError('spacing_type must be a string')

        if not isinstance(letter_spacing, float):
            raise TypeError('letter_spacing must be a float')

        if not isinstance(word_spacing, float):
            raise TypeError('word_spacing must be a float')

        if not isinstance(stretch, (int, basestring)):
            raise TypeError('stretch must be an int or a string')

        #----------------------------------------------------------------------
        # Argument Value Checking
        #----------------------------------------------------------------------
        if isinstance(weight, int):
            if not (-1 <= weight <= 99):
                raise ValueError('weight must be -1 <= weight <= 99')
        else:
            weight = weight.lower()
            if weight not in _weight_map:
                msg = 'weight must be one of %s' % _weight_map.keys()
                raise ValueError(msg)
            else:
                weight = _weight_map[weight]

        style = style.lower()
        if style not in _style_set:
            raise ValueError('style must be one of %s' % list(_style_set))
        
        family_hint = family_hint.lower()
        if family_hint not in _family_hint_set:
            msg = 'family_hint must be one of %s' % list(_family_hint_set)
            raise ValueError(msg)
        
        spacing_type = spacing_type.lower()
        if spacing_type not in _spacing_set:
            msg = 'spacing_type must be one of %s' % list(_spacing_set)
            raise ValueError(msg)
        
        if isinstance(stretch, int):
            if not (1 <= stretch <= 4000):
                raise ValueError('stretch must be 1 <= stretch <= 4000')
        else:
            stretch = stretch.lower()
            if stretch not in _stretch_map:
                msg = 'stretch must be one of %s' % _stretch_map.keys()
                raise ValueError(msg)
            else:
                stretch = _stretch_map[stretch]
        
        vals = (family, point_size, weight, style, underline, strikethrough,
                family_hint, spacing_type, letter_spacing, word_spacing,
                stretch)
        
        return tuple.__new__(cls, vals)
    
    def __repr__(self):
        templ = dedent("""\
        Font(
            family         =    %s
            point_size     =    %s
            weight         =    %s
            style          =    %s
            underline      =    %s
            strikethrough  =    %s
            family_hint    =    %s
            spacing_type   =    %s
            letter_spacing =    %s
            word_spacing   =    %s
            stretch        =    %s
        )
        """)
        return templ % self

    def __str__(self):
        return self.__repr__()
            
    def __nonzero__(self):
        return self != self.default_font
        
    def clone(self, family=None, point_size=None, weight=None, style=None, 
        underline=None, strikethrough=None, family_hint=None, 
        spacing_type=None, letter_spacing=None, word_spacing=None, 
        stretch=None):

        these = (family, point_size, weight, style, underline,
                 strikethrough, family_hint, spacing_type, letter_spacing,
                 word_spacing, stretch)

        vals = ((this if this is not None else other) 
                for (this, other) in zip(these, self))

        return Font(*vals)

    @property
    def family(self):
        return self[0]
    
    @property
    def point_size(self):
        return self[1]
    
    @property
    def weight(self):
        return self[2]
    
    @property
    def style(self):
        return self[3]
    
    @property
    def underline(self):
        return self[4]
    
    @property
    def strikethrough(self):
        return self[5]
    
    @property
    def family_hint(self):
        return self[6]
    
    @property
    def spacing_type(self):
        return self[7]
    
    @property
    def letter_spacing(self):
        return self[8]
    
    @property
    def word_spacing(self):
        return self[9]
    
    @property
    def stretch(self):
        return self[10]
             

# Create an instance of a default font for comparison purposes
Font.default_font = Font()


class FontTrait(StyleTrait):
    
    def create_default(self, obj, name):
        return Font()
    
    def convert(self, obj, name, value):
        if isinstance(value, basestring):
            try:
                font = Font.from_string(value)
            except (ValueError, TypeError):
                font = self.create_default(obj, name)
        elif isinstance(value, Font):
            font = value
        else:
            font = self.create_default(obj, name)
        return font

