#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import urllib

from .qt_abstract_image import QtAbstractImage

class QtLocationImage(QtAbstractImage):
    """ Base class for images which get their data from a specified location.
    
    This class is not meant to be instantiated.
    
    """
    #: The location of the image
    _location = None
    
    #--------------------------------------------------------------------------
    # Setup methods
    #--------------------------------------------------------------------------
    def create(self, tree):
        """ Initializes the location of the image.

        """
        super(QtLocationImage, self).create(tree)
        self.set_location(tree['location'])
    
    #--------------------------------------------------------------------------
    # Message Handlers
    #--------------------------------------------------------------------------
    def on_action_set_location(self, content):
        """ Handle the 'set_location' action from the Enaml widget

        """
        print 'set location', content
        self.set_location(content['location'])
    
    def on_action_reload(self, content):
        """ Handle the 'reload' action from the Enaml widget

        """
        self.load_image()
    
    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_location(self, location):
        """ Set the url where the image can be found, and load it
        
        """
        self._location = location
        self.load_image()


class QtURLImage(QtLocationImage):
    """ A Qt4 implementation of an Enaml URLImage
    
    """
    _data = None
    
    def load_image(self):
        """ Get the image data and load it into the QPixmap
        
        We rely on Qt's automatic filetype detection for the data.
        
        """
        print 'loading image'
        data = self._get_data()
        self.widget().loadFromData(data)
        print 'data set', self.widget().size()
        self._data = data
    
    def _get_data(self):
        """ Download the image data from the supplied URL
        
        """
        print self._location
        if self._location is not None:
            response = urllib.urlopen(self._location)
            # read in data in megabyte-sized chunks
            data = []
            while True:
                chunk = response.read(1<<20)
                if not chunk:
                    break
                data.append(chunk)
            print data[0][:10]
            return b''.join(data)


class QtFileImage(QtLocationImage):
    """ A Qt4 implementation of an Enaml FileImage
    
    """
    
    def load_image(self):
        """ Get the image data and load it into the QPixmap
        
        We rely on Qt's automatic filetype detection for the data.
        
        """
        if self._location is not None:
            self.widget().load(self.location)
