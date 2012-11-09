.. _employee:


Sue Mary tutorial
==============================================================================

This tutorial shows how we can build more complex and dynamic user interfaces
based on |Enaml|. It introduces the concepts of constraints and validators. It
sets up a GUI to edit employee details.


Here is the |Enaml| file (:download:`download here
<../../../examples/tutorial/employee/employee_view.enaml>`):

.. literalinclude:: ../../../examples/tutorial/employee/employee_view.enaml
    :language: python


Here is the Python code (:download:`download here
<../../../examples/tutorial/employee/employee.py>`):

.. literalinclude:: ../../../examples/tutorial/employee/employee.py
    :language: python


``EmployeeForm`` Definition block
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

This block summarizes most of the concepts seen in the previous tutorial. It
creates a new enamldef based on the Form widget. Two attributes are exposed in
the widget: an ``employee`` attribute and a ``show_employer`` boolean value that
defaults to True. The form itself contains a set of 
:py:class:`~enaml.widgets.label.Label`
with their associated :py:class:`~enaml.widgets.field.Field`.

Using validation on fields
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

The ``Home phone:`` field must be validated to make sure the user can't insert
a phone number that is not valid. The user interface must also signal the user
that the current entry is valid or not.

A `PhoneNumberValidator` class implements the ``validate(...)`` method of the
:py:class:`~enaml.validation.Validator` abstract class. If the validation succeeds the
returned value of the validate call is a standardized formatted text.


.. literalinclude:: ../../../examples/tutorial/employee/phone_validator.py
    :language: python

In the Field definition, every time the text get set with a properly validated
entry, the employee phone attribute is updated. ::

    Field:
        validator = PhoneNumberValidator()
        text << '(%s) %s-%s' % employee.phone
        text ::
            match = validator.proper.match(text)
            if match:
                area = match.group(1)
                prefix = match.group(2)
                suffix = match.group(3)
                employee.phone = tuple(map(int, (area, prefix, suffix)))
 

Dynamic interaction with widgets
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

The widget attributes all support the special |Enaml| operators. One can thus
assign the result of arbitrary Python code to interact with the status of the
widget.::

   Label:
        text = 'Password:'
    Field:
        echo_mode << 'password' if not pw_cb.checked else 'normal'
        text :: print 'Password:', text
    Label:
        text = 'Show Password:'
    CheckBox:
        id: pw_cb
        checked = False


In this example, the user can active or deactivate the echo
mode of the password Field based on the state of another widget, the password CheckBox.
The user can refer to the password :py:class:`~enaml.widgets.check_box.CheckBox` using the `id` if the widget.


Visibility is controled with the visible attribute of the widgets. In the
`EmployeeMainView`, the btm_box visibility is connected to the
top_form.show_employer attribute. |Enaml| will take care of the related
relayout issues. See the constraints section for more information.

The very same pattern is used in the `EmployerForm` to enable or disable a
group of Fields baesd on a CheckBox.


Customizing your layout
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

Once you have created the components of your main view, you can assemble them
using the differeent containers:

 * :py:class:`~enaml.widgets.container.Container`,
 * :py:class:`~enaml.widgets.form.Form`,
 * :py:class:`~enaml.widgets.group_box.GroupBox`

Those widgets take care of aranging the layout of the child widgets using a set
of constraints. In this tutorial, the only one that defines constraints is the
outer container::

    Container:
        constraints << [
            vertical(
                top, top_box, btm_box.when(btm_box.visible), spacer, bottom
            ),
            horizontal(left, spacer.flex(), top_box, spacer.flex(), right),
            horizontal(left, spacer.flex(), btm_box, spacer.flex(), right),
            align('midline', top_form, btm_form, clear_invisible=False)
        ]

The constraints attribute of the :py:class:`~enaml.widgets.container.Container`
is populated with a list of constraints. The user expresses how he wants the
layout to be aranged:

 * A vertical list of widgets with the top_box on top of the btm_box
 * ...
