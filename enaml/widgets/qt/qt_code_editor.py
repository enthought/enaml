#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from qt import QtGui

from pyface.ui.qt4.code_editor.code_widget import CodeWidget

from .qt_text_editor import QtTextEditor

from ..code_editor import AbstractTkCodeEditor


class QtCodeEditor(QtTextEditor, AbstractTkCodeEditor):
    """ A Qt implementation of a code editor.

    QtCodeEditor uses the PyFace CodeWidget to provide a code editor widget.
    """

    #--------------------------------------------------------------------------
    # SetupMethods
    #--------------------------------------------------------------------------
    def create(self):
        """ Creates the underlying CodeWidget.

        """
        self.widget = CodeWidget(parent=self.parent_widget())
