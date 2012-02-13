#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from abc import ABCMeta, abstractmethod

from traits.api import HasStrictTraits

from ..styling.color import ColorTrait
from ..styling.font import FontTrait


class AbstractTkStylable(object):
    """ The abstract toolkit interface for a stylable component.

    """
    __metaclass__ = ABCMeta
    
    @abstractmethod
    def shell_bg_color_changed(self, color):
        """ The change handler for the 'bg_color' attribute on the shell
        object. Sets the background color of the internal widget to the 
        given color.
        
        """
        raise NotImplementedError
    
    @abstractmethod
    def shell_fg_color_changed(self, color):
        """ The change handler for the 'fg_color' attribute on the shell
        object. Sets the foreground color of the internal widget to the 
        given color. For some widgets this may do nothing.

        """
        raise NotImplementedError
    
    @abstractmethod
    def shell_font_changed(self, font):
        """ The change handler for the 'font' attribute on the shell
        object. Sets the font of the internal widget to the given font.
        For some widgets this may do nothing.

        """
        raise NotImplementedError


class Stylable(HasStrictTraits):
    """ A mixin class which defines common style themes that certain 
    classes of widgets will wish to support.

    """
    #: The background color of the widget.
    bg_color = ColorTrait
    
    #: The foreground color of the widget.
    fg_color = ColorTrait
    
    #: The font used for the widget.
    font = FontTrait

