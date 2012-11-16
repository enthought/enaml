#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
#from base64 import b64encode

from traits.api import Bool, Unicode, Tuple#, Instance

from enaml.core.trait_types import EnamlEvent

from .control import Control
#from ..noncomponents.image.abstract_image import AbstractImage
#from ..noncomponents.image import ImageFromFile


class AbstractButton(Control):
    """ A base class which provides functionality common for several
    button-like widgets.

    """
    #: The text to use as the button's label.
    text = Unicode

    #: The icon to use for the button.
    #icon = Instance(AbstractImage, ImageFromFile(''))

    #: The size to use for the icon.
    icon_size = Tuple

    #: Whether or not the button is checkable. The default is False.
    checkable = Bool(False)

    #: Whether a checkable button is currently checked.
    checked = Bool(False)

    #: Fired when the button is pressed then released. The payload will
    #: be the current checked state.
    clicked = EnamlEvent

    #: Fired when a checkable button is toggled. The payload will be
    #: the current checked state.
    toggled = EnamlEvent

    #: How strongly a component hugs it's contents' width. Buttons hug
    #: their contents' width weakly by default.
    hug_width = 'weak'

    #--------------------------------------------------------------------------
    # Initialization
    #--------------------------------------------------------------------------
    def snapshot(self):
        """ Returns the snapshot for an abstract button.

        """
        snap = super(AbstractButton, self).snapshot()
        snap['text'] = self.text
        snap['checkable'] = self.checkable
        snap['checked'] = self.checked
        snap['icon_size'] = self.icon_size
        #snap['icon'] = self.icon.as_dict()
        return snap

    def bind(self):
        """ Bind the change handlers for an abstract button.

        """
        super(AbstractButton, self).bind()
        self.publish_attributes('text', 'checkable', 'checked', 'icon_size')
        #self.on_trait_change(self._send_icon, 'icon')

    #--------------------------------------------------------------------------
    # Message Handling
    #--------------------------------------------------------------------------
    def on_action_clicked(self, content):
        """ Handle the 'clicked' action from the UI widget.

        The content will contain the current checked state.

        """
        checked = content['checked']
        self.set_guarded(checked=checked)
        self.clicked(checked)

    def on_action_toggled(self, content):
        """ Handle the 'toggled' action from the UI widget.

        The payload will contain the current checked state.

        """
        checked = content['checked']
        self.set_guarded(checked=checked)
        self.toggled(checked)

