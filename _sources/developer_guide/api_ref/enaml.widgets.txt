Widgets
===============================================================================

An Enaml widget is a toolkit-independent abstraction.
Each GUI toolkit that Enaml supports is a set of widgets that
have been implemented and exist in the :mod:`enaml.widgets` submodule.
A widget interface is not tied to any particular implementation.

Interface
---------

An Enaml widget's interface describes the attributes and events that the
widget exposes as its API. Enaml orchestrates communication between
user-facing views and the underlying graphical toolkits.

*Standard interfaces*

.. inheritance-diagram::
    enaml.widgets.base_component.BaseComponent
    enaml.widgets.bounded_date.BoundedDate
    enaml.widgets.bounded_datetime.BoundedDatetime
    enaml.widgets.calendar.Calendar
    enaml.widgets.check_box.CheckBox
    enaml.widgets.combo_box.ComboBox
    enaml.widgets.component.Component
    enaml.widgets.container.Container
    enaml.widgets.control.Control
    enaml.widgets.date_edit.DateEdit
    enaml.widgets.datetime_edit.DatetimeEdit
    enaml.widgets.enable_canvas.EnableCanvas
    enaml.widgets.field.Field
    enaml.widgets.html.Html
    enaml.widgets.image.Image
    enaml.widgets.label.Label
    enaml.widgets.push_button.PushButton
    enaml.widgets.radio_button.RadioButton
    enaml.widgets.slider.Slider
    enaml.widgets.spin_box.SpinBox
    enaml.widgets.table_view.TableView
    enaml.widgets.toggle_control.ToggleControl
    enaml.widgets.traitsui_item.TraitsUIItem
    enaml.widgets.window.Window
    enaml.widgets.form.Form
    enaml.widgets.group_box.GroupBox
    enaml.widgets.dialog.Dialog
    enaml.widgets.progress_bar.ProgressBar
    :parts: 1

Implementation
--------------

The available backends provide concrete versions of Enaml widget
interfaces. An interface utilizes an implementation-specific
class, which wraps an actual toolkit widget.


*Standard Implementations*

.. inheritance-diagram::
    enaml.widgets.bounded_date.AbstractTkBoundedDate
    enaml.widgets.bounded_datetime.AbstractTkBoundedDatetime
    enaml.widgets.calendar.AbstractTkCalendar
    enaml.widgets.check_box.AbstractTkCheckBox
    enaml.widgets.combo_box.AbstractTkComboBox
    enaml.widgets.component.AbstractTkComponent
    enaml.widgets.container.AbstractTkContainer
    enaml.widgets.control.AbstractTkControl
    enaml.widgets.date_edit.AbstractTkDateEdit
    enaml.widgets.datetime_edit.AbstractTkDatetimeEdit
    enaml.widgets.enable_canvas.AbstractTkEnableCanvas
    enaml.widgets.field.AbstractTkField
    enaml.widgets.html.AbstractTkHtml
    enaml.widgets.image.AbstractTkImage
    enaml.widgets.label.AbstractTkLabel
    enaml.widgets.push_button.AbstractTkPushButton
    enaml.widgets.radio_button.AbstractTkRadioButton
    enaml.widgets.slider.AbstractTkSlider
    enaml.widgets.spin_box.AbstractTkSpinBox
    enaml.widgets.table_view.AbstractTkTableView
    enaml.widgets.toggle_control.AbstractTkToggleControl
    enaml.widgets.traitsui_item.AbstractTkTraitsUIItem
    enaml.widgets.window.AbstractTkWindow
    enaml.widgets.form.AbstractTkForm
    enaml.widgets.group_box.AbstractTkGroupBox
    enaml.widgets.dialog.AbstractTkDialog
    enaml.widgets.progress_bar.AbstractTkProgressBar
    :parts: 1

Standard Widgets
----------------

Abstract base widgets
^^^^^^^^^^^^^^^^^^^^^

.. autosummary::
    :toctree: widgets
    :template: widget.rst

    enaml.widgets.component.Component
    enaml.widgets.container.Container
    enaml.widgets.control.Control
    enaml.widgets.toggle_control.ToggleControl
    enaml.widgets.bounded_date.BoundedDate

Basic widgets
^^^^^^^^^^^^^

.. autosummary::
    :toctree: widgets
    :template: widget.rst

    enaml.widgets.calendar.Calendar
    enaml.widgets.check_box.CheckBox
    enaml.widgets.combo_box.ComboBox
    enaml.widgets.push_button.PushButton
    enaml.widgets.radio_button.RadioButton
    enaml.widgets.field.Field
    enaml.widgets.image.Image
    enaml.widgets.label.Label
    enaml.widgets.slider.Slider
    enaml.widgets.spin_box.SpinBox
    enaml.widgets.datetime_edit.DatetimeEdit
    enaml.widgets.date_edit.DateEdit
    enaml.widgets.progress_bar.ProgressBar

Container widgets
^^^^^^^^^^^^^^^^^

.. autosummary::
    :toctree: widgets
    :template: widget.rst

    enaml.widgets.window.Window
    enaml.widgets.dialog.Dialog
    enaml.widgets.form.Form
    enaml.widgets.group_box.GroupBox

Special widgets
^^^^^^^^^^^^^^^

.. autosummary::
    :toctree: widgets
    :template: widget.rst

    enaml.widgets.html.Html
    enaml.widgets.traitsui_item.TraitsUIItem
    enaml.widgets.enable_canvas.EnableCanvas
    enaml.widgets.table_view.TableView
