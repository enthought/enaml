#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt.QtGui import QWidget, QPainter, QPixmap
from .qt_constraints_widget import QtConstraintsWidget
from .image.qt_abstract_image import QtAbstractImage


class QImageView(QWidget):
    """ A custom QWidget that will paint a QPixmap as an image. The
    api is similar to QLabel, but with a few more options to control
    how the image scales.

    """
    def __init__(self, parent=None):
        """ Initialize a QImageView.

        Parameters
        ----------
        parent : QWidget or None, optional
            The parent widget of this image viewer.

        """
        super(QImageView, self).__init__(parent)
        self._pixmap = None
        self._scaled_contents = False
        self._preserve_aspect_ratio = False
        self._allow_upscaling = False

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def paintEvent(self, event):
        """ A custom paint event handler which draws the image according
        to the current size constraints.

        """
        pixmap = self._pixmap
        if pixmap is None:
            return

        pm_size = pixmap.size()
        pm_width = pm_size.width()
        pm_height = pm_size.height()
        if pm_width == 0 or pm_height == 0:
            return 

        evt_rect = event.rect()
        evt_x = evt_rect.x()
        evt_y = evt_rect.y()
        evt_width = evt_rect.width()
        evt_height = evt_rect.height()

        if not self._scaled_contents:
            # If the image isn't scaled, it is centered if possible.
            # Otherwise, it's painted at the origin and clipped.
            paint_x = max(0, int((evt_width / 2. - pm_width / 2.) + evt_x))
            paint_y = max(0, int((evt_height / 2. - pm_height / 2.) + evt_y))
            paint_width = pm_width
            paint_height = pm_height
        else:
            # If the image *is* scaled, it's scaled size depends on the 
            # size of the paint area as well as the other scaling flags.
            if self._preserve_aspect_ratio:
                pm_ratio = float(pm_width) / pm_height
                evt_ratio = float(evt_width) / evt_height
                if evt_ratio >= pm_ratio:
                    if self._allow_upscaling:
                        paint_height = evt_height
                    else:
                        paint_height = min(pm_height, evt_height)
                    paint_width = int(paint_height * pm_ratio)
                else:
                    if self._allow_upscaling:
                        paint_width = evt_width
                    else:
                        paint_width = min(pm_width, evt_width)
                    paint_height = int(paint_width / pm_ratio)
            else:
                if self._allow_upscaling:
                    paint_height = evt_height
                    paint_width = evt_width
                else:
                    paint_height = min(pm_height, evt_height)
                    paint_width = min(pm_width, evt_width)
            # In all cases of scaling, we know that the scaled image is
            # no larger than the paint area, and can thus be centered.
            paint_x = int((evt_width / 2. - paint_width / 2.) + evt_x)
            paint_y = int((evt_height / 2. - paint_height / 2.) + evt_y)
        
        # Finally, draw the pixmap into the calculated rect.
        painter = QPainter(self)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        painter.drawPixmap(paint_x, paint_y, paint_width, paint_height, pixmap)

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def sizeHint(self):
        """ Returns a appropriate size hint for the image based on the
        underlying QPixmap.

        """
        pixmap = self._pixmap
        if pixmap is not None:
            return pixmap.size()
        return super(QImageView, self).sizeHint()

    def pixmap(self):
        """ Returns the underlying pixmap for the image view.

        """
        return self._pixmap

    def setPixmap(self, pixmap):
        """ Set the pixmap to use as the image in the widget.

        Parameters
        ----------
        pixamp : QPixmap
            The QPixmap to use as the image in the widget.

        """
        self._pixmap  = pixmap
        self.update()

    def scaledContents(self):
        """ Returns whether or not the contents scale with the widget 
        size.

        """
        return self._scaled_contents

    def setScaledContents(self, scaled):
        """ Set whether the contents scale with the widget size.

        Parameters
        ----------
        scaled : bool
            If True, the image will be scaled to fit the widget size, 
            subject to the other sizing constraints in place. If False,
            the image will not scale and will be clipped as required.

        """
        self._scaled_contents = scaled
        self.update()

    def preserveAspectRatio(self):
        """ Returns whether or not the aspect ratio of the image is 
        maintained during a resize.

        """
        return self._preserve_aspect_ratio

    def setPreserveAspectRatio(self, preserve):
        """ Set whether or not to preserve the image aspect ratio.

        Parameters
        ----------
        preserve : bool
            If True then the aspect ratio of the image will be preserved
            if it is scaled to fit. Otherwise, the aspect ratio will be
            ignored.

        """
        self._preserve_aspect_ratio = preserve
        self.update()

    def allowUpscaling(self):
        """ Returns whether or not the image can be scaled greater than
        its natural size.

        """
        return self._allow_upscaling

    def setAllowUpscaling(self, allow):
        """ Set whether or not to allow the image to be scaled beyond
        its natural size.

        Parameters
        ----------
        allow : bool
            If True, then the image may be scaled larger than its 
            natural if it is scaled to fit. If False, the image will
            never be scaled larger than its natural size. In either
            case, the image may be scaled smaller.

        """
        self._allow_upscaling = allow
        self.update()


class QtImageView(QtConstraintsWidget):
    """ A Qt4 implementation of an Enaml ImageView widget.

    """
    #: The internal cached size hint which is used to determine whether
    #: or not a size hint updated event should be emitted when the image
    #: in the control changes.
    _cached_size_hint = None
    
    #: the image_id of the image
    _image_id = None

    #: the internally cached QtImage instance
    _image = None

    #--------------------------------------------------------------------------
    # Setup methods
    #--------------------------------------------------------------------------
    def create_widget(self, parent, tree):
        """ Creates the underlying QImageView control.

        """
        return QImageView(parent)
    
    def create(self, tree):
        super(QtImageView, self).create(tree)
        self.set_scale_to_fit(tree['scale_to_fit'])
        self.set_preserve_aspect_ratio(tree['preserve_aspect_ratio'])
        self.set_allow_upscaling(tree['allow_upscaling'])
        self.set_image_id(tree['image_id'])
        

    #--------------------------------------------------------------------------
    # Message Handlers
    #--------------------------------------------------------------------------
    def on_action_set_scale_to_fit(self, content):
        """ Handle the 'set_scale_to_fit' action from the Enaml widget.

        """
        self.set_scale_to_fit(content['scale_to_fit'])

    def on_action_set_preserve_aspect_ratio(self, content):
        """ Handle the 'set_preserve_aspect_ratio' action from the
        Enaml widget

        """
        self.set_preserve_aspect_ratio(content['preserve_aspect_ratio'])

    def on_action_set_allow_upscaling(self, content):
        """ Handle the 'set_allow_upscaling' action from the Enaml
        widget.

        """
        self.set_allow_upscaling(content['allow_upscaling'])
    
    def on_action_set_image_id(self, content):
        """ Handle the 'set_image_id' action from the Enaml widget.

        """
        self.set_image_id(content['image_id'])
    
    def on_action_snap_image_response(self, content):
        """ Handle the 'snap_image_response' action from the Enaml widget.

        """
        obj_id = content['object_id']
        image = QtAbstractImage.lookup_object(obj_id)
        if image is None:
            image = self._builder.build(content, None, self._pipe)
        self.set_image(image)
        

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_scale_to_fit(self, scale_to_fit):        
        """ Sets whether or not the image scales with the underlying 
        control.

        """
        self.widget().setScaledContents(scale_to_fit)

    def set_preserve_aspect_ratio(self, preserve):
        """ Sets whether or not to preserve the aspect ratio of the 
        image when scaling.

        """
        self.widget().setPreserveAspectRatio(preserve)

    def set_allow_upscaling(self, allow):
        """ Sets whether or not the image will scale beyond its natural
        size.

        """
        self.widget().setAllowUpscaling(allow)

    def set_image_id(self, image_id):
        """ Finds the image in the session and sets it on the underlying
        widget.

        """
        self._image_id = image_id
        if image_id is None:
            return
        image = QtAbstractImage.lookup_object(image_id)
        if image is not None:
            self.set_image()
        else:
            # we don't have the image in the client, so ask for it...
            self.send_action('snap_image', {})
    
    def set_image(self, image):
        """ Set the pixmap to the image's QImage.
        
        """
        if self._image is not None:
            self._image.remove_view(self)
        image.add_view(self)
        self._image = image
        self.refresh_image()
    
    def refresh_image(self):
        """ Update the pixmap in response to a change in the image
        
        """
        pixmap = QPixmap.fromImage(self._image.widget())
        self.widget().setPixmap(pixmap)
        self.relayout()
        
        

