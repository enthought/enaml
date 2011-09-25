#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from ..push_button import TestPushButton


class TestQtPushButton(TestPushButton):
    """ QtPushButton tests. """
    
    def test_button_pressed(self):
        """ Press the button programmatically.
        
        """
        self.widget.pressed.emit()
        self.button_pressed()
    
    def test_button_released(self):
        """ Release the button programmatically.
        
        """
        self.widget.released.emit()
        self.button_released()

    def test_button_clicked(self):
        """ Click the button programmatically.
        
        """
        self.widget.clicked.emit()
        self.button_clicked()
        
    def test_button_down(self):
        """ Test the button's `down` attribute.
        
        """
        component = self.component
        widget = self.widget
        
        self.assertEqual(component.down, False)
        widget.pressed.emit()
        self.assertEqual(component.down, True)
        widget.released.emit()
        self.assertEqual(component.down, False)

    def test_button_all_events(self):
        """ Simulate press, release, and click events.
        
        """

        widget = self.widget
        widget.pressed.emit()
        widget.released.emit()
        widget.clicked.emit()
        self.button_all_events()
