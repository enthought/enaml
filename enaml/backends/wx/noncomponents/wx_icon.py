#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import bisect

from .wx_image import WXImage

from ....noncomponents.abstract_icon import AbstractTkIcon


def _scale_size(from_size, to_size):
    """ An internal function used to scale sizes.

    Scales from_size to fit within the confines of to_size as closely as
    possible while maintaining the aspect ratio of from_size.

    Parameters
    ----------
    from_size : (width, height)
        The width, height tuple of integers of the scaling size.
    
    to_size : (width, height)
        The width, height tuple of integers of the bounding size.

    Returns
    -------
    result : (width, height)
        The width, heigh of the properly scaled size.
    
    """
    from_width, from_height = from_size
    to_width, to_height = to_size
    ratio = from_width / float(from_height)
    if abs(from_width - to_width) < abs(from_height - to_height):
        out_width = to_width
        out_height = int(out_width / ratio)
    else:
        out_height = to_height
        out_width = int(out_height * ratio)
    return (out_width, out_height)


class _IconEntry(object):
    """ An object which holds information about an icon. 

    Instances of this class are used internally by the WXIcon class to
    implement its icon data store.

    """
    def __init__(self, image, mode, state):
        """ Initialize an _IconEntry.

        Parameters
        ----------
        image : WXImage
            The WXImage instance held by this icon entry.
        
        mode : string
            The mode of the given image.
            
        state : string
            The state of the given image.
        
        """
        self.image = image
        self.mode = mode
        self.state = state

    def __lt__(self, other):
        """ Overridden '<' operator. The comparison is based on the 
        size of the entry and allows for instances to be sorted.

        """
        return self.size < other.size

    @property
    def size(self):
        """ Returns the (width, height) size of the underlying image.

        """
        return self.image.size

    @property
    def area(self):
        """ Returns the width * height area of the entry.

        """
        size = self.size
        return size[0] * size[1]


class WXIcon(AbstractTkIcon):
    """ A Wx implementation of AbstractTkIcon
    
    """
    def __init__(self):
        """ Initialize a WxIcon.

        """
        # The list of IconEntry instances for this icon. The are kept
        # in sorted order according to their size.
        self._entries = []

    #--------------------------------------------------------------------------
    # Private Methods
    #--------------------------------------------------------------------------
    def _match(self, size, mode, state):
        """ A private method which searches for a suitable _IconEntry
        for the given size, mode, and state. Returns None if no match
        can be made.

        """
        area = size[0] * size[1]
        match = None
        for entry in self._entries:
            if entry.mode == mode and entry.state == state:
                if entry.area >= area:
                    match = entry
                    break
        return match
    
    def _best_match(self, size, mode, state):
        """ A private method which returns the best _IconEntry match for
        the request, or None if no match can be made.

        """
        # Try the default match and then cycle through the various states
        # in an intelligent fashion trying to find any other match. This 
        # logic is more or less identical to QIcon's internal logic.
        match = self._match(size, mode, state)
        if match is None:
            opp_state = 'off' if state == 'on' else 'on'
            if mode == 'disabled' or mode == 'selected':
                opp_mode = 'selected' if mode == 'disabled' else 'disabled'
                new_info = (
                    ('normal', state),
                    ('active', state),
                    (mode, opp_state),
                    ('normal', opp_state),
                    ('active', opp_state),
                    (opp_mode, state),
                    (opp_mode, opp_state),
                )
            else:
                opp_mode = 'active' if mode == 'normal' else 'normal'
                new_info = (
                    (opp_mode, state),
                    (mode, opp_state),
                    (opp_mode, opp_state),
                    ('disabled', state),
                    ('selected', state),
                    ('disabled', opp_state),
                    ('selected', opp_state),
                )
            for new_mode, new_state in new_info:
                match = self._match(size, new_mode, new_state)
                if match is not None:
                    break
        return match

    #--------------------------------------------------------------------------
    # Abstract API Implementation
    #--------------------------------------------------------------------------
    @classmethod
    def from_file(cls, path):
        """ Create a new icon from a file on disk.

        Parameters
        ----------
        path : string
            The path to the image to use for the default mode and state.
            
        Returns
        -------
        result : AbstractTkIcon
            An new icon instance.

        """
        img = WXImage.from_file(path)
        return cls.from_image(img)
    
    @classmethod
    def from_image(cls, image):
        """ Create a new icon from an instance of AbstractTkImage using
        the default 'normal' and 'on' states.
                
        Parameters
        ----------
        image : AbstractTkImage
            An appropriate instance of AbstractTkImage to use for the
            default mode and state.

        Returns
        -------
        result : AbstractTkIcon
            An new icon instance.
            
        """
        if not isinstance(image, WXImage):
            msg = 'Image must be an instance of WXImage. Got %s instead.'
            raise TypeError(msg % type(image))
        new_icon = cls()
        new_icon.add_image(image, 'normal', 'on')
        return new_icon

    def get_image(self, size, mode='normal', state='on'):
        """ Get an appropriate image instance for the requested size, 
        mode and state.
        
        Parameters
        ----------
        size : (width, height)
            The size of the requested image. The returned image may
            be smaller, but will never be larger than this size.
            
        mode : string
            The mode of the requested image.
            
        state : string
            The state of the requested image.
        
        Returns
        -------
        result : AbstractTkImage
            An appropriate image instance.

        """
        match = self._best_match(size, mode, state)
        if match is None:
            res = WXImage()
        else:
            res = match.image
            actual_size = match.size
            if actual_size != size:
                scaled_size = _scale_size(actual_size, size)
                res = res.scale(scaled_size)
        return res

    def add_image(self, image, mode='normal', state='on'):
        """ Add an image instance for use by the icon with the given 
        mode and state.
        
        Parameters
        ----------
        image : AbstractTkImage
            An appropriate image instance.
            
        mode : string, optional
            The mode of the image. The default is 'normal'.
            
        state : string, optional
            The state of the image. The default is 'on'.
        
        """
        if not isinstance(image, WXImage):
            msg = 'Image must be an instance of WXImage. Got %s instead.'
            raise TypeError(msg % type(image))
        size = image.size
        match = self._match(size, mode, state)
        if match is not None:
            match.image = image
        else:
            entry = _IconEntry(image, mode, state)
            bisect.insort(self._entries, entry)

    def actual_size(self, size, mode='normal', state='on'):
        """ Returns the actual size for the requested size, mode, and
        state.

        The returned size may be smaller but will never be larger.

        Parameters
        ----------
        size : (width, height)
            The size of the requested image. The returned image may
            be smaller, but will never be larger than this size.
            
        mode : string, optional
            The mode of the requested image. The default is 'normal'.
            
        state : string, optional
            The state of the requested image. The default is 'on'.
        
        Returns
        -------
        result : (width, height)
            The actual size for the requested size. If no suitable
            match can be found, the result will be (-1, -1).

        """
        match = self._best_match(size, mode, state)
        if match is None:
            res = (-1, -1)
        else:
            res = match.size
            if res != size:
                res = _scale_size(res, size)
        return res
        
    def available_sizes(self, mode='normal', state='on'):
        """ Returns the available image sizes for the given mode and 
        state.
        
        Sizes other than these may be requested, but the implemetation 
        may scale down the image on the fly to the requested size.
        
        Parameters
        ----------
        mode : string, optional
            The requested image mode. The default is 'normal'.
            
        state : string, optional
            The requested image state. The default is 'on'.
        
        """
        sizes = []
        for entry in self._entries:
            if entry.mode == mode and entry.state == state:
                sizes.append(entry.size)
        return sizes

