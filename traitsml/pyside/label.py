from enthought.traits.api import Any, DelegatesTo

from PySide import QtGui

from ..constants import Align
from .element import Element
from .mixins import GeneralWidgetMixin


class LabelWidget(GeneralWidgetMixin, QtGui.QLabel):
    pass


class Label(Element):
    
    # The alignment of the text in the label - XXX create some enums
    alignment = DelegatesTo('abstract_obj')

    # The format of the text in the label - XXX create some enums
    format = DelegatesTo('abstract_obj')

    # The number of pixels of indentation - Int
    indent = DelegatesTo('abstract_obj') 

    # The number of pixels of margin - Int
    margin = DelegatesTo('abstract_obj')

    # The text in the label - Str
    text = DelegatesTo('abstract_obj')

    # Whether text should wrap at word break - Bool
    wrap = DelegatesTo('abstract_obj')

    #--------------------------------------------------------------------------
    # Creation Handler
    #--------------------------------------------------------------------------
    def create_widget(self):
        return LabelWidget() 
    
    #--------------------------------------------------------------------------
    # Initialization
    #--------------------------------------------------------------------------
    def init_attributes(self):
        super(Label, self).init_attributes()
        self.init_alignment()
        self.init_format()
        self.init_indent()
        self.init_margin()
        self.init_text()
        self.init_wrap()

    def init_alignment(self):
        pass
            
    def init_format(self):
        pass

    def init_indent(self):
        pass

    def init_margin(self):
        pass

    def init_text(self):
        self.widget.setText(self.text)

    def init_wrap(self):
        self.widget.setWordWrap(self.wrap)

    #--------------------------------------------------------------------------
    # Change Handlers
    #--------------------------------------------------------------------------
    def _alignment_changed(self):
        pass
    
    def _format_changed(self):
        pass

    def _indent_changed(self):
        self.widget.setIndent(self.indent)

    def _margin_changed(self):
        self.widget.setMargin(self.margin)

    def _text_changed(self):
        self.widget.setText(self.text)

    def _wrap_changed(self):
        self.widget.setWordWrap(self.wrap)


