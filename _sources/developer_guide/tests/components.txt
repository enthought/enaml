Component Testing
=================

.. automodule:: enaml.tests.widgets


EnamlTestCase
-------------

.. autoclass:: enaml.tests.widgets.enaml_test_case.EnamlTestCase

The enaml_test_case module provides also two decorators to assist in the
creation of Enaml compoenent test suites

.. autofunction:: enaml.tests.widgets.enaml_test_case.required_method

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

.. autoclass:: enaml.tests.widgets.wx.wx_test_assistant.WXTestAssistant

Qt
^^

.. autoclass:: enaml.tests.widgets.qt.qt_test_assistant.QtTestAssistant


Widget testing classes
----------------------

.. autosummary::
    :toctree: widgets
    :template: widget_test.rst

    enaml.tests.widgets.calendar.TestCalendar
    enaml.tests.widgets.check_box.TestCheckBox
    enaml.tests.widgets.combo_box.TestComboBox
    enaml.tests.widgets.push_button.TestPushButton
    enaml.tests.widgets.radio_button.TestRadioButton
    enaml.tests.widgets.field.TestField
    enaml.tests.widgets.label.TestLabel
    enaml.tests.widgets.slider.TestSlider
    enaml.tests.widgets.spin_box.TestSpinBox
    enaml.tests.widgets.html.TestHtml
    enaml.tests.widgets.datetime_edit.TestDatetimeEdit
    enaml.tests.widgets.date_edit.TestDateEdit
