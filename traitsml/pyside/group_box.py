from enthought.traits.api import DelegatesTo

from PySide import QtCore, QtGui

from ..constants import Align
from .element import Element
from .mixins import GeneralWidgetMixin


# These are the only alignments supported by QGroupBox
ALIGN_MAP = {Align.DEFAULT: QtCore.Qt.AlignLeft,
             Align.LEFT: QtCore.Qt.AlignLeft,
             Align.RIGHT: QtCore.Qt.AlignRight,
             Align.HCENTER: QtCore.Qt.AlignHCenter}


class GroupBoxWidget(GeneralWidgetMixin, QtGui.QGroupBox):
    pass


class GroupBox(Element):

    # The aligment of the title of the group box. - Enum of Align values
    alignment = DelegatesTo('abstract_obj')

    # Whether or not the group box is checkable. Checking a 
    # group box will enable and disable it's children. - Bool
    checkable = DelegatesTo('abstract_obj')

    # Whether or not the group box is checked. - Bool
    checked = DelegatesTo('abstract_obj')

    # A flat group box will not draw sunkend or borders. - Bool
    flat = DelegatesTo('abstract_obj')

    # The title of the group box - Str
    title = DelegatesTo('abstract_obj')

    #--------------------------------------------------------------------------
    # Creation Handler
    #--------------------------------------------------------------------------
    def create_widget(self):
        return GroupBoxWidget()

    #--------------------------------------------------------------------------
    # Initialization
    #--------------------------------------------------------------------------
    def init_widget(self):
        super(GroupBox, self).init_widget()
        self.widget.toggled.connect(self._on_toggled)
    
    def init_attributes(self):
        super(GroupBox, self).init_attributes()
        self.init_alignment()
        self.init_checkable()
        self.init_checked()
        self.init_flat()
        self.init_title()

    def init_alignment(self):
        q_alignment = ALIGN_MAP.get(self.alignment)
        if q_alignment is None:
            raise ValueError('Invalid GroupBox alignment.')
        self.widget.setAlignment(q_alignment)

    def init_checkable(self):
        self.widget.setCheckable(self.checkable)

    def init_checked(self):
        self.widget.setChecked(self.checked)

    def init_flat(self):
        self.widget.setFlat(self.flat)

    def init_title(self):
        self.widget.setTitle(self.title)

    #--------------------------------------------------------------------------
    # Change Handlers
    #--------------------------------------------------------------------------
    def _alignment_changed(self):
        q_alignment = ALIGN_MAP.get(self.alignment)
        if q_alignment is None:
            raise ValueError('Invalid GroupBox alignment.')
        self.widget.setAlignment(q_alignment)

    def _checkable_changed(self):
        self.widget.setCheckable(self.checkable)

    def _checked_changed(self):
        self.widget.setChecked(self.checked)

    def _flat_changed(self):
        self.widget.setFlat(self.flat)

    def _title_changed(self):
        self.widget.setTitle(self.title)
    
    #--------------------------------------------------------------------------
    # Slots
    #--------------------------------------------------------------------------
    def _on_toggled(self):
        self.checked = self.widget.isChecked()


