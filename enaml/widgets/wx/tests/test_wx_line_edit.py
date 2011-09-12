# -*- coding: utf-8 -*-
import unittest
import weakref
import sys

import wx

from enaml.widgets.wx.wx_line_edit import WXLineEdit


class WidgetParent(object):
    """Mock parent class"""

    def __init__(self):

        self.app = wx.App(0)
        self.widget = wx.Frame(None)

    def __call__(self):
        return weakref.ref(self)


class testWXLineEdit(unittest.TestCase):
    """Testsuite for WXLineEdit

    The widget is tested in isolation without the traitaml boilerplate
    """

    def setUp(self):
        # setup an empty application
        parent = WidgetParent()

        # setup widgets

        self.lineedit = WXLineEdit()

        # simulating initialization
        self.lineedit.parent_ref = parent()
        self.lineedit.create_widget()
        self.lineedit.init_attributes()
        self.lineedit.text = 'test line edit'
        self.lineedit.read_only = False

    def checkPosition(self, pos):
        """Check if the position is correct at the widget and the enaml
        object"""

        widget = self.lineedit.toolkit_widget()

        self.assertEqual(widget.GetInsertionPoint(), pos,
            "Current position (widget) should be {0} and not {1}".\
            format(pos, widget.GetInsertionPoint()))
        tml_pos = self.lineedit.cursor_position
        self.assertEqual(widget.GetInsertionPoint(), tml_pos,
                "Current position between traits: {0} and "
                "widget: {1} do not match". format(tml_pos,
                                                widget.GetInsertionPoint()))

    def checkText(self, text):
        """Check if the position is correct at the widget and the enaml
        object"""

        widget = self.lineedit.toolkit_widget()

        self.assertEqual(text, widget.GetValue())
        self.assertEqual(self.lineedit.text, widget.GetValue())

    def checkSelectedText(self, text):
        """Check if the position is correct at the widget and the enaml
        object"""

        widget = self.lineedit.toolkit_widget()

        self.assertEqual(text, widget.GetStringSelection())
        self.assertEqual(self.lineedit.selected_text,
                            widget.GetStringSelection())

    def testInitialContents(self):
        """Check the values of the WXLineEdit"""

        widget = self.lineedit.toolkit_widget()

        # text
        self.checkText('test line edit')

        # read only flag
        self.assertTrue(widget.IsEditable(),
                'The line edit should be editable')

        # max length
        self.assertEqual(self.lineedit.max_length, sys.maxint,
            'Max length should be {0} and not {1}'.format(sys.maxint,
                                                self.lineedit.max_length))

        # current position should be at the end of the starting string
        self.checkPosition(0)

    def testTextChange(self):
        """Test changing the text of a WXLineEdit"""

        new_text = 'This a new text'
        self.lineedit.text = new_text

        self.checkText(new_text)

    def testReadonly(self):
        """Test setting readonly style setting"""

        widget = self.lineedit.toolkit_widget()

        self.lineedit.read_only = True
        self.assertFalse(widget.IsEditable(),
                'The text should read only')

        self.lineedit.read_only = False
        self.assertTrue(widget.IsEditable(),
            'The text should be editable')

    def testMaxlength(self):
        """Test the use of the maxlength attribute"""

        self.lineedit.max_length = 5
        self.lineedit.text = "This is a longer line"

        self.checkText('This ')

    def testCursor(self):
        """Test the use of the current_cursor attribute"""

        # set cursor position
        self.lineedit.cursor_position = 5
        self.checkPosition(5)

    def testEnd(self):
        """Test end function"""

        widget = self.lineedit.toolkit_widget()

        # set cursor position
        self.lineedit.cursor_position = 5

        # move to the end
        self.lineedit.end()
        self.checkPosition(14)

        # set cursor position
        self.lineedit.cursor_position = 5

        # select until the end
        self.lineedit.end(mark=True)
        self.checkPosition(5)
        self.assertEqual(widget.GetSelection(), (5, 14))
        self.assertEqual(self.lineedit.selected_text, 'line edit')

    def testHome(self):
        """Test home function"""

        widget = self.lineedit.toolkit_widget()

        # set cursor position
        self.lineedit.cursor_position = 5

        # move to the start
        self.lineedit.home()
        self.checkPosition(0)

        # set cursor position
        self.lineedit.cursor_position = 5

        # select from start
        self.lineedit.home(mark=True)
        self.checkPosition(0)
        self.assertEqual(widget.GetSelection(), (0, 5))
        self.assertEqual(self.lineedit.selected_text, 'test ')

    def testModifiedFlag(self):
        """Test the modified flag functionality"""

        widget = self.lineedit.toolkit_widget()

        # programatically change text
        self.lineedit.text = 'new text'
        self.assertEqual('new text', widget.GetValue())
        self.assertFalse(self.lineedit.modified)

    def testInsertText(self):
        """Test inserting text"""

        self.lineedit.cursor_position = 4
        self.lineedit.insert(' my words')

        # check text
        self.checkText('test my words line edit')

        self.checkPosition(13)

    def testUndoRedo(self):
        """Text UndoRedo functionality"""

        self.lineedit.cursor_position = 4
        self.lineedit.insert(' my words')

        # Check first undo
        # ----------------
        self.lineedit.undo()

        self.checkText('test line edit')
        self.checkPosition(4)

        # Check second redo
        # ----------------

        # move cursor
        self.lineedit.cursor_position = 5
        # redo
        self.lineedit.redo()

        self.checkText('test my words line edit')
        # in redo the change appears as a selection so the cursor is placed at
        # the beginning!
        self.checkPosition(4)

    def testSelectAll(self):
        """Test selecting all the text"""

        self.lineedit.cursor_position = 6

        self.lineedit.select_all()

        self.checkSelectedText('test line edit')
        self.checkPosition(0)

    def testDeselect(self):
        """Testing the de-select function"""

        self.lineedit.cursor_position = 4

        self.lineedit.set_selection(2, 6)
        self.lineedit.deselect()

        self.checkSelectedText('')
        self.checkPosition(2)

    def testClear(self):
        """Testing the clear function"""

        self.lineedit.cursor_position = 4

        self.lineedit.set_selection(2, 6)
        self.lineedit.clear()

        self.checkPosition(0)
        self.checkSelectedText('')
        self.checkText('')

    def testBackspace(self):
        """Testing the clear function"""

        self.lineedit.cursor_position = 4
        self.lineedit.backspace()

        self.checkText('tes line edit')
        self.checkPosition(3)

        self.lineedit.set_selection(1, 5)
        self.lineedit.backspace()

        self.checkText('tine edit')
        self.checkPosition(1)

    def testDelete(self):
        """Testing the clear function"""

        self.lineedit.cursor_position = 4
        self.lineedit.delete()

        self.checkText('testline edit')
        self.checkPosition(4)

        self.lineedit.set_selection(1, 5)
        self.lineedit.delete()

        self.checkText('tine edit')
        self.checkSelectedText('')
        self.checkPosition(1)



if __name__ == '__main__':
    unittest.main()
