#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Array, Enum

from .abstract_image import AbstractImage


class ArrayImage(AbstractImage):
    """ An image class which holds the raw bytes of an image in a numpy array
    
    This class is particularly useful when you have modifiable raw image data
    on the server and needs to send to the client.
    
    """
    #: a MxNx3 or MxNx4 array of uint8 containing the raw bytes of the image
    data = Array(dtype='uint8', shape=(None, None, (3,4)))
    
    #: the image channel layout: 'RGB', 'RGBA', or 'ARGB'
    format = Enum(None, 'RGB', 'RGBA', 'ARGB')
    
    #--------------------------------------------------------------------------
    # Initialization
    #--------------------------------------------------------------------------
    def snapshot(self):
        """ Create a snapshot of the current state of the DataImage
        
        Messages
        --------
        
        This builds the contents of a snapshot message with from superclass
        methods, as well as:
            
        data : bytes
            An encoding of the data buffer of the array.
        format : 'RGB', 'RGBA', or 'ARGB'
            The channel layout of the array.
        size : tuple of (width, height)
            The width and height of the image.
        
        """
        snap = super(ArrayImage, self).snapshot()
        if self.data is not None:
            snap['data'] = self.action_pipe.encode_binary(self.data.data)
            if self.format is None:
                self._infer_format()
            snap['format'] = self.format
            snap['size'] = self.data.shape[1::-1]
        return snap

    #--------------------------------------------------------------------------
    # Messaging Methods
    #--------------------------------------------------------------------------
    def set_image_array(self, data, format=None):
        """ Change the image data, emitting a 'set_data' message
        
        Parameters
        ----------
        
        data : MxNx3 or MxNx4 array of uint8
            The raw bytes of the image.
        format : str
            The optional channel format of the raw image. If this is not
            provided, then the class will attempt to guess the format based
            on the data.
        
        Messages
        --------
        
        If the session exists, this sends a 'set_image_array' action message
        with content:
            
        data : bytes
            An encoding of the data buffer of the array.
        format : 'RGB', 'RGBA', or 'ARGB'
            The channel layout of the array.
        size : tuple of (width, height)
            The width and height of the image.
        
        """
        self.data = data
        if format is None:
            self._infer_format()
        else:
            self.format = format
        content = {
            'data': self.action_pipe.encode_binary(data.data),
            'format': self.format,
            'size': self.data.shape[1::-1],
        }
        self.send_action('set_image_array', content)
        
    #--------------------------------------------------------------------------
    # Internal Methods
    #--------------------------------------------------------------------------
    def _infer_format(self):
        """ Attempt to infer the channel format from the data.
        
        We assume that NxMx3 arrays are RGB, and the NxMx4 arrays are RGBA.
        
        """
        if self.data is not None:
            if self.data.shape[-1] == 3:
                self.format = 'RGB'
            elif self.data.shape[-1] == 4:
                self.format = 'RGBA'

