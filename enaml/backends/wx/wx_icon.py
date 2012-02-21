#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------

from ...components.abstract_icon import AbstractTkIcon

from .wx_pixmap import WXPixmap

class WXIcon(AbstractTkIcon):
    """ Collection of Pixmap instances for display in a component
    
    The Icon class allows the user to specify different images for different
    states of the icon, so that a widget can select the image which is most
    appropriate for display in the widget.
    
    The Icon class can specify modes and states, which toolkit objects may use
    to select which pixmap to use for display.  The modes used by the wx backend
    are:
        
        normal: for a control in its normal mode
        
        disabled: for a control which is disabled or greyed-out
    
    Not every mode is used by every backend.  The state of an icon is either:
        
        on: the normal or checked form of the icon
        
        off: the unchecked form of the icon
    
    """
    PixmapClass = WXPixmap

    def __init__(self):
        self._pixmaps = {}
        self._scaled_pixmaps = {}
    
    
    def get_pixmap(self, size=(None, None), mode='normal', state='on'):
        """ Get an appropriate image instance for the requested size, mode and state
        
        """
        if (mode, state) in self._pixmaps:
            if size in self._pixmaps[(mode, state)]:
                return self._pixmaps[(mode, state)][size]
            # have we scaled this to this size before?
            if size in self._scaled_pixmaps.get((mode, state), {}):
                return self._scaled_pixmaps[(mode, state)][size]
            # get largest pixmap and scale to size
            max_size = max(self._pixmaps[(mode, state)])
            base_pixmap = self._pixmaps[(mode, state)][max_size]
            scaled_pixmap = base_pixmap.scale(size)
            self._scaled_pixmaps.setdefault((mode, state), {})[size] = scaled_pixmap
            return scaled_pixmap
        elif mode != 'normal' or state != 'on':
            return self.get_pixmap(size)
        else:
            return WXPixmap()
    
    
    def set_pixmap(self, pixmap, mode='normal', state='on'):
        """ Set the appropriate Pixmap instance for the requested size, mode and state
        
        If no images have been set for the corresponding 'normal' and 'on' states
        then this will also set the image as a default for those states as well.
        
        Arguments
        ---------
        
        pixmap : backend AbstractTkPixmap subclass
            The size of the requested pixmap.
            
        mode : str
            The mode of the requested pixmap.
            
        state : str
            The state of the requested pixmap.
        
        """
        if not isinstance(pixmap, self.PixmapClass):
            raise ValueError('pixmap argument must be an instance of enaml.backends.wx.wx_pixmap.WXPixmap, ' +
                str(pixmap) + ' provided.')
        size = pixmap.size
        self._pixmaps.setdefault((mode, state), {})[size] = pixmap
        if size == max(self._pixmaps[(mode, state)]):
            # blow away the scaling cache
            self._scaled_pixmaps[(mode, state)] = {}
        # fill in some other defaults
        if not ('normal', 'on') in self._pixmaps:
            self._pixmaps.setdefault(('normal', 'on'), {})[size] = pixmap
        if not (mode, 'on') in self._pixmaps:
            self._pixmaps.setdefault((mode, 'on'), {})[size] = pixmap
        if not ('normal', state) in self._pixmaps:
            self._pixmaps.setdefault(('normal', state), {})[size] = pixmap

    
    def available_sizes(self, mode='normal', state='on'):
        """ Return the available Pixmap instance sizes for the given mode and state
        
        Other sizes can be requested, but the implemetation may scale the image
        on the fly to the requested size.
        
        Arguments
        ---------
            
        mode : str
            The mode of the requested pixmap.
            
        state : str
            The state of the requested pixmap.
        
        """
        return self._pixmaps.get((mode, state), {}).keys()
    
