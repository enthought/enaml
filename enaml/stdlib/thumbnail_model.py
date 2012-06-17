#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from collections import namedtuple
from functools import wraps

from enaml.core.toolkit import Toolkit
from enaml.core.item_model import AbstractListModel, ALIGN_HCENTER, ALIGN_VCENTER


# A named tuple representing a thumbnail. It contains the 'name' to show
# below the thumbnail in a view. The 'image' object from which to create
# the thumbnail, and any 'metadata' to associate with the thumbnail for
# use in other parts of an application.
Thumbnail = namedtuple('Thumbnail', 'name image metadata')


def _refresh_data(func):
    """ A method decorator which will trigger a refresh of all data in 
    a list model. This assumes that the data in the list model is in 
    the zero column.

    """
    @wraps(func)
    def closure(self, *args, **kwargs):
        parent = None
        top_left = self.index(0, 0, parent)
        bottom_right = self.index(self.row_count(parent) - 1, 0, parent)
        res = func(self, *args, **kwargs)
        self.notify_data_changed(top_left, bottom_right)
        return res
    return closure


class ThumbnailModel(AbstractListModel):
    """ A concrete list model implementation which displays a list of
    thumbnails.

    """
    def __init__(self, thumbs=None):
        """ Initialize a ThumbnailModel

        Parameters
        ----------
        thumbs : list, optional
            An initial list of Thumbnail objects to be used by the model.

        """
        self._thumbs = thumbs[:] if thumbs is not None else []
        self._toolkit = Toolkit.active_toolkit()
        self._icon_cls = self._toolkit['Icon']

    #--------------------------------------------------------------------------
    # Abstract List Model Implementation
    #--------------------------------------------------------------------------
    def row_count(self, index):
        """ Returns the number of thumbnails in the current thumbnail
        list.

        """
        if index is None:
            return len(self._thumbs)
        return 0

    def data(self, index):
        """ Returns the name for the thumbnail at the given index.

        """
        return self._thumbs[index.row].name

    def alignment(self, index):
        """ Returns the alignment for the given row. Thumbnail text
        is centered in the item.

        """
        return ALIGN_HCENTER | ALIGN_VCENTER
    
    def decoration(self, index):
        """ Returns the icon for the given row. The icons are created
        on the fly from the images contained in the thumbnails.

        """
        image = self._thumbs[index.row].image
        return self._icon_cls.from_image(image)

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _insert(self, idx, thumb):
        """ Inserts the given thumbnail or list of thumbnails at the 
        given index and triggers the appropriate data refresh.

        """
        if isinstance(thumb, Thumbnail):
            self.begin_insert_rows(None, idx, idx)
            self._thumbs.insert(idx, thumb)
            self.end_insert_rows(None, idx, idx)
        else:
            last = idx + len(thumb) - 1
            self.begin_insert_rows(None, idx, last)
            old = self._thumbs
            new = old[:idx] + thumb + old[idx:]
            self._thumbs = new
            self.end_insert_rows(None, idx, last)

    def _append(self, thumb):
        """ Appends the given thumbnail to the model and triggers the
        appropriate data refresh.

        """
        idx = len(self._thumbs)
        self.begin_insert_rows(None, idx, idx)
        self._thumbs.append(thumb)
        self.end_insert_rows(None, idx, idx)

    def _extend(self, thumbs):
        """ Extends the model with the given thumbnails and triggers
        the appropriate data refresh.

        """
        idx = len(self._thumbs)
        last = idx + len(thumbs) - 1
        self.begin_insert_rows(None, idx, last)
        self._thumbs.extend(thumbs)
        self.end_insert_rows(None, idx, last)

    def _remove(self, idx, count):
        """ Removes the given number of thumbnails starting at the
        given index.

        """
        last = idx + count - 1
        self.begin_remove_rows(None, idx, last)
        del self._thumbs[idx:last+1]
        self.end_remove_rows(None, idx, last)

    def _set_thumbnails(self, thumbs):
        """ Resets the model using the given thumbnails.

        """
        self.begin_reset_model()
        self._thumbs = thumbs[:]
        self.end_reset_model()

    def _clear(self):
        """ Clears the internal list of thumbnails and resets the model.

        """
        self.begin_reset_model()
        self._thumbs = []
        self.end_reset_model()
        
    #--------------------------------------------------------------------------
    # Public Methods
    #--------------------------------------------------------------------------
    def insert(self, idx, thumb):
        """ Insert the given thumbnail(s) at the specified index and
        trigger the appropriate refresh.

        Parameters
        ----------
        idx : int
            The index where to insert the thumbnail(s).

        thumb : Thumbnail or list of Thumbnails
            The thumbnail(s) to insert into the model. If a list is
            given, the thumbnails will be inserted in order.

        Notes
        -----
        This method is thread safe. The actual update will occur on the
        main gui thread. It is thus safe to use a thread to perform the 
        thumbnail creation and then request the update.

        """
        self._toolkit.app.call_on_main(self._insert, idx, thumb)

    def append(self, thumb):
        """ Append the given thumbnail to the model and trigger the
        appropriate refresh. 
        
        Parameters
        ----------
        thumb : Thumbnail
            The thumbnail to append to the model.

        Notes
        -----
        This method is thread safe. The actual update will occur on the
        main gui thread. It is thus safe to use a thread to perform the 
        thumbnail creation and then request the update.

        """
        self._toolkit.app.call_on_main(self._append, thumb)

    def extend(self, thumbs):
        """ Extend the model with the given thumbnails and trigger the
        appropriate refresh.
        
        Parameters
        ----------
        thumbs : list of Thumbnails
            The thumbnails to add to the end of the model.

        Notes
        -----
        This method is thread safe. The actual update will occur on the
        main gui thread. It is thus safe to use a thread to perform the 
        thumbnail creation and then request the update.

        """
        self._toolkit.app.call_on_main(self._extend, thumbs)

    def remove(self, idx, count):
        """ Remove the specified thumbnails from the model.

        Parameters
        ----------
        idx : int
            The starting index of the chunk of thumbnails to remove.

        count : int
            The number of thumbnails to remove from the model.

        Notes
        -----
        This method is thread safe. The actual update will occur on the
        main gui thread. It is thus safe to use a thread to perform the 
        thumbnail creation and then request the update.

        """
        self._toolkit.app.call_on_main(self._remove, idx, count)

    def thumbnail(self, index):
        """ Returns the thumbnail for the given model index.

        """
        return self._thumbs[index.row]
        
    def thumbnails(self):
        """ Returns the thumbnails in the model.

        Returns
        -------
        result : list of Thumbnails
            The thumbnails in use by the model.

        Notes
        -----
        The returned list is a copy of internal list of thumbnails.
        It is safe to modify the returned list in-place as it will 
        have no effect on the model.

        """
        return self._thumbs[:]

    def set_thumbnails(self, thumbs):
        """ Reset the model with the provided thumbnails.

        Parameters
        ----------
        thumbs : list of Thumbnails
            The thumbnails to use in the model. Old thumbnails will
            be discarded.

        Notes
        -----
        This method is thread safe. The actual update will occur on the
        main gui thread. It is thus safe to use a thread to perform the 
        thumbnail creation and then request the update.

        """
        self._toolkit.app.call_on_main(self._set_thumbnails, thumbs)

    def clear(self):
        """ Clear the model of all thumbnails and trigger the 
        appropriate refresh.

        """
        self._toolkit.app.call_on_main(self._clear)

