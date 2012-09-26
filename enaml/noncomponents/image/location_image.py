#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Str, File

from .abstract_image import AbstractImage


class LocationImage(AbstractImage):
    """ An abstract image class which points to an image at a location
    
    """
    #: the location of the data
    location = Str
    
    #--------------------------------------------------------------------------
    # Initialization
    #--------------------------------------------------------------------------
    def snapshot(self):
        """ Create a snapshot of the current state of the DataImage
        
        """
        snap = super(LocationImage, self).snapshot()
        snap['location'] = self.location
        return snap
    
    def bind(self):
        super(LocationImage, self).bind()
        self.publish_attributes('location')
    
    #--------------------------------------------------------------------------
    # Messaging Methods
    #--------------------------------------------------------------------------
    def reload(self):
        """ Send a message to the client to reload the image from the location
        
        """
        # XXX Should make this an EnamlEvent?
        self.send_action('reload', {})


class URLImage(LocationImage):
    """ An image class which points to an image at a URL
    
    The URL is contained in the location.
    
    """
    # this uses the same server-side implementation as FileImage, but
    # the client implementation will be different.
    location = Str


class FileImage(LocationImage):
    """ An image class which points to an image in a file
    
    If this is used by a remote client, it is presumed that the file is visible
    to the client.  The file does not need to be visible to the server.
    
    """
    # this uses the same server-side implementation as URLImage, but
    # the client implementation will be different.
    location = File


