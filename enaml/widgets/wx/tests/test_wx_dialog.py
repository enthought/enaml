import unittest

import wx

from ..wx_dialog import WXDialog
from ...dialog import Dialog
from ....enums import DialogResult


class TestWXDialog(unittest.TestCase):
    """Tests for WXDialog.
    
    """

    def setUp(self):
        """ Set up widgets.
        
        """
        self.dialog = Dialog(toolkit_impl=WXDialog())

    def test_dialog_active(self):
        """ Check that the dialog's 'active' attribute is set properly.
        
        """
        dialog = self.dialog
        self.assertEqual(dialog.active, False, 'Dialog not shown yet.')
        dialog.show()
        self.assertEqual(dialog.active, True, 'Dialog should be active.')

    
    def test_intial_result(self):
        """ Check that a dialog rejected by default.
        
        """
        self.assertEqual(self.dialog.result, DialogResult.REJECTED,
                'Dialog should be rejected by default.')
    
    def test_accept_result(self):
        """ Test the 'result' attribute of an accepted dialog.
        
        """
        dialog = self.dialog
        dialog.accept()
        self.assertEqual(dialog.result, DialogResult.ACCEPTED)

if __name__ == '__main__':
    app = wx.App()
    unittest.main()
