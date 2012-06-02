#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import wx

from .wx_control import WXControl

from ...components.image_view import AbstractTkImageView


class wxBitmapWidget(wx.Panel):
    """ A wx.Panel subclass which paints a provided wx.Bitmap. 

    This differs from wx.StaticBitmap in that it provides the option to
    scale the provided bitmap to the bounds of the widget. If the widget
    is set to scale its contents, low quality scaling will occur during
    resize, with a high quality pass performed once resizing as finished.

    """
    def __init__(self, parent):
        """ Initialize a wxBitmapWidget.

        Parameters
        ----------
        parent : wx.Window
            The wx.Window object which serves as the widget parent.
        
        """
        super(wxBitmapWidget, self).__init__(parent)
        self._bitmap = None
        self._scaled_contents = False
        self._preserve_aspect_ratio = False
        self._allow_upscaling = False
        self._resize_timer = None
        self._resizing = False
        self.Bind(wx.EVT_PAINT, self.OnPaint)

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def OnPaint(self, event):
        """ The paint event handler for the widget.

        """
        bmp = self._bitmap
        if bmp is None:
            return

        bmp_width, bmp_height = bmp.GetWidth(), bmp.GetHeight()
        if bmp_width == 0 or bmp_height == 0:
            return

        evt_x = 0
        evt_y = 0
        evt_width, evt_height = self.GetSize().asTuple()

        if not self._scaled_contents:
            # If the image isn't scaled, it is centered if possible.
            # Otherwise, it's painted at the origin and clipped.
            paint_x = max(0, int((evt_width / 2. - bmp_width / 2.) + evt_x))
            paint_y = max(0, int((evt_height / 2. - bmp_height / 2.) + evt_y))
            paint_width = bmp_width
            paint_height = bmp_height
        else:
            # If the image *is* scaled, it's scaled size depends on the 
            # size of the paint area as well as the other scaling flags.
            if self._preserve_aspect_ratio:
                bmp_ratio = float(bmp_width) / bmp_height
                evt_ratio = float(evt_width) / evt_height
                if evt_ratio >= bmp_ratio:
                    if self._allow_upscaling:
                        paint_height = evt_height
                    else:
                        paint_height = min(bmp_height, evt_height)
                    paint_width = int(paint_height * bmp_ratio)
                else:
                    if self._allow_upscaling:
                        paint_width = evt_width
                    else:
                        paint_width = min(bmp_width, evt_width)
                    paint_height = int(paint_width / bmp_ratio)
            else:
                if self._allow_upscaling:
                    paint_height = evt_height
                    paint_width = evt_width
                else:
                    paint_height = min(bmp_height, evt_height)
                    paint_width = min(bmp_width, evt_width)
            # In all cases of scaling, we know that the scaled image is
            # no larger than the paint area, and can thus be centered.
            paint_x = int((evt_width / 2. - paint_width / 2.) + evt_x)
            paint_y = int((evt_height / 2. - paint_height / 2.) + evt_y)

        # Scale the bitmap if needed, using a faster method if the
        # image is currently being resized
        if paint_width != bmp_width or paint_height != bmp_height:
            img = bmp.ConvertToImage()
            if self._resizing:
                quality = wx.IMAGE_QUALITY_NORMAL
            else:
                quality = wx.IMAGE_QUALITY_HIGH
            img.Rescale(paint_width, paint_height, quality)
            bmp = wx.BitmapFromImage(img)

        # Finally, draw the bitmap into the computed location
        dc = wx.PaintDC(self)
        dc.DrawBitmap(bmp, paint_x, paint_y)

    def OnResize(self, event):
        """ The resize event handler for the widget.

        This method is only bound and called when content scaling is
        enabled. It starts(restarts) a timer to perform a high quality
        scaled repaint when resizing is finished.

        """
        self._resizing = True
        self._resize_timer.Start(60, True)

    def OnResizeEnd(self, event):
        """ The repaint timer event handler.

        This method is only bound and called when content scaling is
        enabled and resizing has completed. It triggers a high quality
        repaint.

        """
        self._resizing = False
        self.Refresh()

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def GetBestSize(self):
        """ Overridden method to return the size of the bitmap as the 
        best size for the widget.

        """
        bmp = self._bitmap
        return wx.Size(bmp.GetWidth(), bmp.GetHeight())

    def GetBestSizeTuple(self):
        """ Overridden method to return the size of the bitmap as the 
        best size for the widget.

        """
        return self.GetBestSize().asTuple()

    def GetBitmap(self, bitmap):
        """ Get the underlying wx.Bitmap used to paint the control.

        Returns
        -------
        result : wx.Bitmap or None
            The bitmap being used to paint the control, or None if
            no bitmap has been supplied.

        """
        return self._bitmap

    def SetBitmap(self, bitmap):
        """ Set the underlying wx.Bitmap and refresh the widget.

        Parameters
        ----------
        bitmap : wx.Bitmap
            The bitmap to paint on the widget.
        
        """
        self._bitmap = bitmap
        self.Refresh()

    def GetScaledContents(self):
        """ Whether or not the bitmap is scaled to fit the bounds.

        Returns
        -------
        result : bool
            Whether or not the bitmap is scaled to fit the bounds of
            the widget.
        
        """
        return self._scaled_contents
    
    def SetScaledContents(self, scaled):
        """ Set whether or not the bitmap should be scaled to fit the
        bounds of the widget.

        Parameters
        ----------
        scaled : bool
            Whether or not to scale the bitmap to fit the bounds of the
            widget.
        
        """
        if scaled:
            if not self._scaled_contents:
                self._scaled_contents = True
                self._resize_timer = wx.Timer(self)
                self.Bind(wx.EVT_TIMER, self.OnResizeEnd)
                self.Bind(wx.EVT_SIZE, self.OnResize)
        else:
            if self._scaled_contents:
                self._scaled_contents = False
                self._timer = None
                self.Unbind(wx.EVT_TIMER, handler=self.OnResizeEnd)
                self.Unbind(wx.EVT_SIZE, handler=self.OnResize)
        self.Refresh()

    def GetPreserveAspectRatio(self):
        """ Returns whether or not the aspect ratio of the image is 
        maintained during a resize.

        """
        return self._preserve_aspect_ratio

    def SetPreserveAspectRatio(self, preserve):
        """ Set whether or not to preserve the image aspect ratio.

        Parameters
        ----------
        preserve : bool
            If True then the aspect ratio of the image will be preserved
            if it is scaled to fit. Otherwise, the aspect ratio will be
            ignored.

        """
        self._preserve_aspect_ratio = preserve
        self.Refresh()
        
    def GetAllowUpscaling(self):
        """ Returns whether or not the image can be scaled greater than
        its natural size.

        """
        return self._allow_upscaling

    def SetAllowUpscaling(self, allow):
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
        self.Refresh()


class WXImageView(WXControl, AbstractTkImageView):
    """ A Wx implementation of ImageView.

    """
    #: The internal cached size hint which is used to determine whether
    #: of not a size hint updated event should be emitted when the text
    #: in the label changes
    _cached_size_hint = None

    #--------------------------------------------------------------------------
    # Setup methods
    #--------------------------------------------------------------------------
    def create(self, parent):
        """ Creates the underlying wxBitmapWidget control.

        """
        self.widget = wxBitmapWidget(parent)

    def initialize(self):
        """ Initializes the attributes on the underlying control.

        """
        super(WXImageView, self).initialize()
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
        """ Sets the image on the underlying wxBitmapWidget.

        """
        bmp = image.as_wxBitmap() if image is not None else None
        self.widget.SetBitmap(bmp)
        # Emit a size hint updated event if the size hint has actually
        # changed. This is an optimization so that a constraints update
        # only occurs when the size hint has actually changed. This 
        # logic must be implemented here so that the label has been
        # updated before the new size hint is computed. Placing this
        # logic on the shell object would not guarantee that the label
        # has been updated at the time the change handler is called.
        cached = self._cached_size_hint
        hint = self._cached_size_hint = self.size_hint()
        if cached != hint:
            self.shell_obj.size_hint_updated()
    
    def set_scale_to_fit(self, scale_to_fit):        
        """ Sets whether or not the image scales with the underlying 
        control.

        """
        self.widget.SetScaledContents(scale_to_fit)

    def set_preserve_aspect_ratio(self, preserve):
        """ Sets whether or not to preserve the aspect ratio of the 
        image when scaling.

        """
        self.widget.SetPreserveAspectRatio(preserve)

    def set_allow_upscaling(self, allow):
        """ Sets whether or not the image will scale beyond its natural
        size.

        """
        self.widget.SetAllowUpscaling(allow)

