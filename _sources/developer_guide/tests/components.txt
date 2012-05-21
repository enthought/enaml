Component Testing
=================

.. automodule:: enaml.tests.components


EnamlTestCase
-------------

.. autoclass:: enaml.tests.components.enaml_test_case.EnamlTestCase

The enaml_test_case module provides also two decorators to assist in the
creation of Enaml compoenent test suites

.. autofunction:: enaml.tests.components.enaml_test_case.required_method

TestAssistant classes
---------------------

For each toolkit backend there exist a TestAssistant class which is
responisble for setting the attrributes to the correct toolkit. In some
cases these classes contain utility methods that are specific to the current
toolkit. The toolkit specific tests for each component have to inherit first
from the toolikit test assistant class and then the generic widget component
test suite.

WX
^^

.. autoclass:: enaml.tests.components.wx.wx_test_assistant.WXTestAssistant

Qt
^^

.. autoclass:: enaml.tests.components.qt.qt_test_assistant.QtTestAssistant


Widget testing classes
----------------------

.. autosummary::
    :toctree: widgets
    :template: widget_test.rst

    enaml.tests.components.calendar.TestCalendar
    enaml.tests.components.check_box.TestCheckBox
    enaml.tests.components.combo_box.TestComboBox
    enaml.tests.components.date_edit.TestDateEdit
    enaml.tests.components.datetime_edit.TestDatetimeEdit
    enaml.tests.components.dialog.TestDialog
    enaml.tests.components.field.TestField
    enaml.tests.components.html.TestHtml
    enaml.tests.components.group_box.TestGroupBox
    enaml.tests.components.label.TestLabel
    enaml.tests.components.operators.TestLessLess
    enaml.tests.components.progress_bar.TestProgressBar
    enaml.tests.components.push_button.TestPushButton
    enaml.tests.components.radio_button.TestRadioButton
    enaml.tests.components.selection_models.TestBaseSelectionModel
    enaml.tests.components.selection_models.TestRowSelectionModel
    enaml.tests.components.slider.TestSlider
    enaml.tests.components.spin_box.TestSpinBox
    enaml.tests.components.toggle_button.TestToggleButton
    enaml.tests.components.window.TestWindow
