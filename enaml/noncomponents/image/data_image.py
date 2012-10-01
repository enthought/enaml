#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import mimetypes

from traits.api import Str

from .abstract_image import AbstractImage
from .util import infer_mimetype


class DataImage(AbstractImage):
    """ An image class which holds the raw bytes of an image in a numpy array
    
    This class is particularly useful when you have modifiable raw image data
    on the server and needs to send to the client.
    
    """
    #: the bytes of the image
    data = Str
    
    #: the mimetype of the image
    mimetype = Str
    
    #--------------------------------------------------------------------------
    # Initialization
    #--------------------------------------------------------------------------
    @classmethod
    def from_file(cls, filename):
        with open(filename, 'rb') as fp:
            data = fp.read()
        mimetype = mimetypes.guess_type(filename)[0] or infer_mimetype(data)
        return cls(data=data, mimetype=mimetype)
    
    def snapshot(self):
        """ Create a snapshot of the current state of the DataImage
        
        Messages
        --------
        
        This builds the contents of a snapshot message with from superclass
        methods, as well as:
            
        data : bytes
            An encoding of the data buffer of the array.
        mimetype : str
            The mimetype of the data.
        
        """
        snap = super(DataImage, self).snapshot()
        if self.action_pipe is not None:
            snap['data'] = self.action_pipe.encode_binary(self.data)
        else:
            snap['data'] = self.data
        snap['mimetype'] = self.mimetype
        return snap
    
    def bind(self):
        super(DataImage, self).bind()
        self.on_trait_change(self._send_data, 'data')

    #--------------------------------------------------------------------------
    # Messaging Methods
    #--------------------------------------------------------------------------
    def _send_data(self):
        """ Change emit a 'set_data' message
        
        Messages
        --------
        
        This sends a 'set_image_array' action message with content:
            
        data : bytes
            An encoding of the data buffer of the array.
        mimetype : str
            The mimetype of the encoded data.
        
        """
        content = {
            'data': self.action_pipe.encode_binary(self.data.data),
            'mimetype': self.mimetype,
        }
        self.send_action('set_data', content)

    #--------------------------------------------------------------------------
    # Traits Handlers
    #--------------------------------------------------------------------------
    def _data_changed(self):
        """ The stored image data changed
        
        We treat the magic number as being a truer representation of the image
        mimetype than file extensions or user-supplied mimetypes.
        
        """
        mimetype = infer_mimetype(self.data)
        if mimetype is not None:
            self.mimetype = mimetype
