.. _tutorial_even_more_widgets:

More on |Enaml| Widgets
===============================================================================

In this tutorial, we take a closer look at some of the widgets available for
building GUI's in |Enaml| by building on the :ref:`John Doe tutorial
<john-doe>`. We will explore some of the things you can do with widgets that
you can't do or that are hard to do in other GUI builders.

This example will use the employee example
:download:`employee_view.enaml <../../../examples/employee/employee_view.enaml>`
to explore these concepts.

.. image:: images/employee.png

Building Views From Parts
-------------------------------------------------------------------------------

The |Enaml| language allows you to define re-usable parts of your view that can
defined separately, and then built into a larger interface as needed.  In the
``employee_view.enaml`` example, the code defines two forms, one for an employee,
and one for an employer (abbreviated here for succinctness)::

    enamldef EmployeeForm(Form):
        attr employee
        attr show_employer: bool = False
        Label:
            text = "First name:"
        Field:
            value := employee.first_name

        # ... etc

        ToggleButton:
            checked := show_employer
            text << ('Hide' if show_employer else 'Show') + ' Employer Details'

    enamldef EmployerForm(Form):
        attr employer
        Label:
            text = "Company:"
        Field:
            value << employer.company_name
            enabled << en_cb.checked
        # ... etc

This sort of |Enaml| code should be fairly familiar to you at this point
(although there are some new things which we will highlight later).
Previously all of our ``enamldef`` operations had used ``MainWindow`` as the
widget that was being extended, but here we are using ``Form``.  Any widget can
be used as the basis for another in an ``enamldef`` command, so you can create
your own custom, re-usable ``Label``s, ``Field``s, ``PushButton``s, etc. using
``enamldef``.

Having defined the two forms, there is a third definition in the .enaml file::

    enamldef EmployeeView(MainWindow):
        id: main
        attr employee

        title << "Employee Record for: %s, %s" % (employee.last_name,
                                                employee.first_name)
        Container:
            constraints << [
                vertical(top, top_box, bottom_box.when(bottom_box.visible), bottom),
                horizontal(left, spacer.flex(), top_box, spacer.flex(), right),
                horizontal(left, spacer.flex(), bottom_box, spacer.flex(), right),
                align('midline', top_form, bottom_form, clear_invisible=False)
            ]
            GroupBox:
                id: top_box
                title = "Personal Details"
                EmployeeForm:
                    id: top_form
                    # We access the employee object through the identifier
                    # 'main' here, because the EmployeeForm also has an
                    # 'employee' attribute declared, and that would be
                    # found first.
                    employee = main.employee
            GroupBox:
                id: bottom_box
                title = "Employer Details"
                visible << top_form.show_employer
                EmployerForm:
                    id: bottom_form
                    employer << employee.boss

This part of the code should be fairly familiar at this point: we have a
``MainWindow`` class which contains a ``Container`` which in turn contains two
``GroupBox`` widgets.  We haven't seen ``GroupBox`` widgets before, but they are
special containers that draw a box around their contents, and have an optional
title.

In the first ``GroupBox`` we see that it's contents are just one ``EmployeeForm``
where the ``employee`` attribute is initialized to ``main.employee``.  This
shows you that once you have defined a new widget type with ``enamldef``, it
can be used just like any other widget, and that you can bind to its attributes
in exactly the same way that you can bind to the attributes of base widget
types.

The second GroupBox is similar, except that it contains an EmployerForm.

Custom Validators
------------------------------------------------------------------------------

In an earlier example we saw that |Enaml| has certain types of ``Field`` that
perform validation.  You can define your own custom validators to check for
specific types of input.  The phone number field in the employee example has
a custom validator::

    Field:
        value := employee.phone
        validator = PhoneNumberValidator()
        bgcolor << 'unacceptable' if not acceptable else 'none'

This validator is imported from
:download:`phone_validator.py <../../../examples/employee/phone_validator.py>`
and looks like this:

.. literalinclude:: ../../../examples/employee/phone_validator.py
    :language: python

A validator has to implement three methods: ``validate``, ``convert`` and
``format``.

The ``validate`` method takes a string which is the current contents of
the widget, and is expected to return one of three values: ``self.ACCEPTABLE``
if the text matches a valid value, ``self.INTERMEDIATE`` if the text does not
match a valid value, but could be a sub-string of a valid value, or
``self.INVALID`` if there is no way that this string could be valid.

The validate method is called on any keypress in the widget, and the value will
only be allowed to be set into the contents of the widget if the response is
either ``ACCEPTABLE`` or ``INTERMEDIATE``.  Since validate methods are called
frequently, they should attempt to be as fast as possible.

The ``convert`` method takes a string which is the current contents of
the widget and converts it to the required type for the model value.
The ``format`` method takes a model value and converts it to a string
representation.
The ``convert`` and ``format`` methods should be inverses, so that
``convert(format(value)) == value``.

Visibility of Widgets and Constraints
------------------------------------------------------------------------------

Looking at the example, you will see that there is a button on the
``EmployeeForm`` that toggles the visibility of the bottom ``GroupBox``.  This
is done via the ``visible`` attribute of the ``GroupBox``.  Most widgets have a
``visible`` attribute that can be changed this way.

When a widget is not visible, it still participates in constraints by default.
However frequently you want to remove invisible widgets from the set of
constraints, and so the constraints helpers, such as ``align`` will automatically
remove invisible widgets from the set of constraints.  In cases where you still
what the constraints to apply, you can set the ``clear_invisible`` flag to
``False`` on the constraints helper::

    align('midline', top_form, bottom_form, clear_invisible=False)

For constraints applied without the use of helper functions, you can use
Python's ... if ... else ... expressions to change the constraints as needed::

    constraints = [top_box.left == bottom_box.left] if bottom_form.visible else []

Additionally, in the constraints above you can see that the vertical layout
constraint::

    vertical(top, top_box, bottom_box.when(bottom_box.visible), bottom)

has the expression ``bottom_box.when(bottom_box.visible)``.  Any widget or
constraint helper can have a ``when`` method appended which contains an
expression which is evaluated as a boolean.  If the expression is true, then
the widget is included by the layout helper, otherwise it is not.  This gives
another convenient way to toggle the participation of widgets in constraints.

More Constraints
------------------------------------------------------------------------------

Looking closely at the constraints of the outermost ``Container``, you may notice
that there is the constraint::

    align('midline', top_form, bottom_form, clear_invisible=False)

``Form`` widgets in |Enaml| have an additional position beyond the usual ones
described in the previous chapter: the 'midline'.  This represents the line
between the left and right-hand columns of widgets.  Without this constraint,
the view looks like this:

.. image:: images/employee_no_midline.png

As you can see, by specifying that the two forms' midlines align, the two forms
look more unified.  This particular sort of alignment can be very tedious to
achieve in a conventional nested box layout system.

Advanced developers who are building their own widget classes can create
additional constraint variables for their widgets.  Read the source code of the
Form widget to see the basics of how to do this.

Other Things to Note
------------------------------------------------------------------------------

In this example you also see a number of different widget types that we have not
seen before:

    DateEdit:
        This is a field type designed for editing Python ``datetime.date``
        objects.

    CheckBox:
        This is a simple checkbox widget that can toggle a value True or False.

    ToggleButton:
        This is a like the checkbox widget in that it toggles a value True or
        False, but instead it looks like a push button.  The button highlights
        when it is True.

Additionally, the Password field shows how to set a field to hide the text
being entered, as you would normally want for a password entry field.




