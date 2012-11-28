#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt.QtGui import QImage
from .qt_object import QtObject


class QtImage(QtObject):

    def create_widget(self, parent, tree):
        return QImage.fromData(tree['data'])

