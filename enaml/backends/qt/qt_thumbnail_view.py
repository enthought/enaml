#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt.QtCore import QSize
from .qt.QtGui import (
    QListView, QStyledItemDelegate, QApplication, QStyleOptionViewItemV4,
    QStyle,
)
from .qt_list_view import QtListView

from ...components.thumbnail_view import AbstractTkThumbnailView


class QThumbnailDelegate(QStyledItemDelegate):
    """ A specialized styled item delegate which returns a size hint
    appropriate for fixed size thumbnails with text below the image.

    """
    def sizeHint(self, option, index):
        """ Returns a size hint appropriate for the thumbnail assuming
        text is drawn below the image.

        """
        # The default implementation of sizeHint for QStyledItemDelegate
        # will change the decoration size set in the option (which is 
        # determined by the iconSize in the ListView) based on the natural
        # size of the icons as supplied by the model (this change happens 
        # in initStyleOption which is called by sizeHint). The problem 
        # with this is that it violates the assumption of uniform size
        # items of the thumbnail and can lead to bizarre rendering effects
        # like clipped text and jumbled thumbnail insertions. To combat
        # these unwanted effects, we reimplement the sizeHint function to
        # be identical to the default implementation, except that we 
        # restore the original decoration size after initing the style
        # option. This helps ensure that the size hint for each item
        # is reported identically (modulo text wrapping effects).
        originalDecorationSize = QSize(option.decorationSize)
        opt = QStyleOptionViewItemV4(option)
        self.initStyleOption(opt, index)
        widget = opt.widget
        style = widget.style() if widget is not None else QApplication.style()
        opt.decorationSize = originalDecorationSize
        styleFlag = QStyle.CT_ItemViewItem
        return style.sizeFromContents(styleFlag, opt, QSize(), widget)


class QThumbnailView(QListView):
    """ A QListView subclass which uses a custom delegate to draw 
    thumbnail images.

    """
    def __init__(self, *args, **kwargs):
        """ Initialize a QThumbnailView.

        This initialization method ensures that the a QThumbnailDelegate
        is properly created and installed on the view.

        Parameters
        ----------
        *args, **kwargs
            The parameters necessary to initialize a QListView.

        """
        super(QThumbnailView, self).__init__(*args, **kwargs)
        self.setItemDelegate(QThumbnailDelegate())


class QtThumbnailView(QtListView, AbstractTkThumbnailView):
    """ A Qt4 implementation of ThumbnailView.

    """
    #--------------------------------------------------------------------------
    # Setup Methods
    #--------------------------------------------------------------------------
    def create(self, parent):
        """ Creates the underlying QThumbnailView widget.

        """
        self.widget = QThumbnailView(parent)

