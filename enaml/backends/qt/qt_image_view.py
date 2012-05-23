#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt.QtGui import QWidget, QPainter
from .qt_control import QtControl

from ...components.image_view import AbstractTkImageView


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

    def sizeHint(self):
        """ Returns a appropriate size hint for the image based on the
        underlying QPixmap.

        """
        pixmap = self._pixmap
        if pixmap is not None:
            return pixmap.size()
        return super(QImageView, self).sizeHint()

    def setPixmap(self, pixmap):
        """ Set the pixmap to use as the image in the widget.

        Parameters
        ----------
        pixamp : QPixmap
            The QPixmap to use as the image in the widget.

        """
        self._pixmap  = pixmap
        self.update()

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

    def paintEvent(self, event):
        """ A custom paint event handler which draws the image according
        to the current size constraints.

        """
        pixmap = self._pixmap
        if pixmap is None:
            return

        evt_rect = event.rect()
        evt_x = evt_rect.x()
        evt_y = evt_rect.y()
        evt_width = evt_rect.width()
        evt_height = evt_rect.height()

        pm_size = pixmap.size()
        pm_width = pm_size.width()
        pm_height = pm_size.height()

        if not self._scaled_contents:
            # If the image isn't scaled, it is centered if possible.
            # Otherwise, it's painted at the origin and clipped.
            paint_x = max(0, int((evt_width / 2. - pm_width / 2.) + evt_x))
            paint_y = max(0, int((evt_height / 2. - pm_height / 2.) + evt_y))
            paint_width = pm_width
            paint_height = pm_height
        else:
            # If the image *is*, it's scaled size depends on the size 
            # of the paint area as well as the other scaling flags.
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


class QtImageView(QtControl, AbstractTkImageView):
    """ A Qt4 implementation of ImageView.

    """
    #: The internal cached size hint which is used to determine whether
    #: or not a size hint updated event should be emitted when the image
    #: in the control changes.
    _cached_size_hint = None

    #--------------------------------------------------------------------------
    # Setup methods
    #--------------------------------------------------------------------------
    def create(self, parent):
        """ Creates the underlying QLabel control.

        """
        self.widget = QImageView(parent)

    def initialize(self):
        """ Initializes the attributes on the underlying control.

        """
        super(QtImageView, self).initialize()
        shell = self.shell_obj
        self.set_image(shell.image)
        self.set_scale_to_fit(shell.scale_to_fit)
        self.set_preserve_aspect_ratio(shell.preserve_aspect_ratio)
        self.set_allow_upscaling(shell.allow_upscaling)

    #--------------------------------------------------------------------------
    # Implementation
    #--------------------------------------------------------------------------
    def shell_image_changed(self, image):
        """ The change handler for the 'image' attribute on the shell 
        component.

        """
        self.set_image(image)
    
    def shell_scale_to_fit_changed(self, scale_to_fit):
        """ The change handler for the 'scale_to_fit' attribute on the 
        shell component.

        """
        self.set_scale_to_fit(scale_to_fit)

    def shell_preserve_aspect_ratio_changed(self, preserve):
        """ The change handler for the 'preserve_aspect_ratio' attribute
        on the shell component.

        """
        self.set_preserve_aspect_ratio(preserve)

    def shell_allow_upscaling_changed(self, allow):
        """ The change handler for the 'allow_upscaling' attribute on 
        the shell component.

        """
        self.set_allow_upscaling(allow)

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_image(self, image):
        """ Sets the image on the underlying QLabel.

        """
        self.widget.setPixmap(image.as_QPixmap())
        # Emit a size hint updated event if the size hint has actually
        # changed. This is an optimization so that a constraints update
        # only occurs when the size hint has actually changed. This 
        # logic must be implemented here so that the control has been
        # updated before the new size hint is computed. Placing this
        # logic on the shell object would not guarantee that the control
        # has been updated at the time the change handler is called.
        cached = self._cached_size_hint
        hint = self._cached_size_hint = self.size_hint()
        if cached != hint:
            self.shell_obj.size_hint_updated()
    
    def set_scale_to_fit(self, scale_to_fit):        
        """ Sets whether or not the image scales with the underlying 
        control.

        """
        self.widget.setScaledContents(scale_to_fit)

    def set_preserve_aspect_ratio(self, preserve):
        """ Sets whether or not to preserve the aspect ratio of the 
        image when scaling.

        """
        self.widget.setPreserveAspectRatio(preserve)

    def set_allow_upscaling(self, allow):
        """ Sets whether or not the image will scale beyond its natural
        size.

        """
        self.widget.setAllowUpscaling(allow)

