#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .enaml_test_case import required_method
from .window import TestWindow


def skip_test(func):
    def closure(self, *args, **kwargs):
        self.skipTest('Skipped')
    return closure


class TestDialog(TestWindow):
    """ Logic for testing Dialogs.

    """

    def setUp(self):
        """ Set up Dialog tests.

        """

        enaml_source = """
enamldef MainView(Dialog):
    name = 'dialog'
    title = 'foo'
"""

        self.view = self.parse_and_create(enaml_source)
        self.component = self.component_by_name(self.view, 'dialog')
        self.widget = self.component.toolkit_widget
        # Don't actually show the dialog.
        self.disable_showing(self.widget)
        # (trait_name, value) log of all trait change events on the Dialog.
        self.event_log = []
        self.component.on_trait_change(self._append_event_handler, 'anytrait')

    def test_initial_active(self):
        """ Test the initial value of the active flag on the Dialog.

        """
        self.assertEquals(self.component.active, False)
    
    def test_result_value(self):
        """ Test the modification of the result value.

        """
        self.assertEquals(self.component.result, 'rejected')
        self.component.accept()
        self.assertEquals(self.component.result, 'accepted')
        self.component.reject()
        self.assertEquals(self.component.result, 'rejected')

    def test_show_close(self):
        """ Test the behavior when showing and closing the dialog.

        """
        self.component.abstract_obj.set_visible(True)
        # Compare sets because the order is unimportant.
        self.assertEquals(set(self.event_log), set([
            ('active', True),
            ('_active', True),
            ('opened', None),
        ]))
        self.event_log = []
        self.component.accept()
        self.assertEquals(set(self.event_log), set([
            ('active', False),
            ('_active', False),
            ('result', 'accepted'),
            ('_result', 'accepted'),
            ('closed', 'accepted'),
        ]))
        self.event_log = []
        self.component.abstract_obj.set_visible(True)
        self.assertEquals(set(self.event_log), set([
            ('active', True),
            ('_active', True),
            ('opened', None),
        ]))
        self.event_log = []
        self.component.reject()
        self.assertEquals(set(self.event_log), set([
            ('active', False),
            ('_active', False),
            ('result', 'rejected'),
            ('_result', 'rejected'),
            ('closed', 'rejected')
        ]))

    @required_method
    def disable_showing(self, widget):
        """ Disable the actual display of the dialog window.

        """
        pass

    def _append_event_handler(self, object, name, old, new):
        """ Append the trait change notification to the event log.

        """
        # XXX this test is fragile since it's collected all trait 
        # change events. Hence we need to filter out certain things
        # we don't care about. FIX THIS TEST!!!!!
        if name == '_relayout_pending':
            return
        self.event_log.append((name, new))

