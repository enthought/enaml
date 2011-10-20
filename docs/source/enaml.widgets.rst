Widgets
=======

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
    enaml.widgets.calendar.Calendar
    enaml.widgets.check_box.CheckBox
    enaml.widgets.combo_box.ComboBox
    enaml.widgets.push_button.PushButton
    enaml.widgets.radio_button.RadioButton
    enaml.widgets.component.Component
    enaml.widgets.container.Container
    enaml.widgets.control.Control
    enaml.widgets.dialog.Dialog
    enaml.widgets.field.Field
    enaml.widgets.form.Form
    enaml.widgets.group.Group
    enaml.widgets.group_box.GroupBox
    enaml.widgets.h_group.HGroup
    enaml.widgets.html.Html
    enaml.widgets.window.Window
    enaml.widgets.panel.Panel
    enaml.widgets.v_group.VGroup
    enaml.widgets.traitsui_item.TraitsUIItem
    enaml.widgets.image.Image
    enaml.widgets.label.Label
    enaml.widgets.toggle_control.ToggleControl
    enaml.widgets.slider.Slider
    enaml.widgets.spacer.Spacer
    enaml.widgets.spin_box.SpinBox
    enaml.widgets.tab_group.TabGroup
    enaml.widgets.stacked_group.StackedGroup
    enaml.widgets.enable_canvas.EnableCanvas
    enaml.widgets.datetime_edit.DatetimeEdit
    enaml.widgets.date_edit.DateEdit
    :parts: 1

Implementation
--------------

The available backends provide concrete versions of Enaml widget
interfaces. An interface utilizes an implementation-specific
class, which wraps an actual toolkit widget.


*Standard Implementations*

.. inheritance-diagram::
    enaml.widgets.calendar.ICalendarImpl
    enaml.widgets.check_box.ICheckBoxImpl
    enaml.widgets.combo_box.IComboBoxImpl
    enaml.widgets.component.IComponentImpl
    enaml.widgets.container.IContainerImpl
    enaml.widgets.push_button.IPushButtonImpl
    enaml.widgets.radio_button.IRadioButtonImpl
    enaml.widgets.control.IControlImpl
    enaml.widgets.dialog.IDialogImpl
    enaml.widgets.field.IFieldImpl
    enaml.widgets.form.IFormImpl
    enaml.widgets.group.IGroupImpl
    enaml.widgets.group_box.IGroupBoxImpl
    enaml.widgets.h_group.IHGroupImpl
    enaml.widgets.html.IHtmlImpl
    enaml.widgets.window.IWindowImpl
    enaml.widgets.panel.IPanelImpl
    enaml.widgets.v_group.IVGroupImpl
    enaml.widgets.traitsui_item.ITraitsUIItemImpl
    enaml.widgets.image.IImageImpl
    enaml.widgets.label.ILabelImpl
    enaml.widgets.toggle_control.IToggleControlImpl
    enaml.widgets.slider.ISliderImpl
    enaml.widgets.spacer.ISpacerImpl
    enaml.widgets.spin_box.ISpinBoxImpl
    enaml.widgets.tab_group.ITabGroupImpl
    enaml.widgets.stacked_group.IStackedGroupImpl
    enaml.widgets.enable_canvas.IEnableCanvasImpl
    enaml.widgets.datetime_edit.IDatetimeEditImpl
    enaml.widgets.date_edit.IDateEditImpl
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
    enaml.widgets.window.Window
    enaml.widgets.toggle_control.ToggleControl

Container widgets
^^^^^^^^^^^^^^^^^

.. autosummary::
    :toctree: widgets
    :template: widget.rst

    enaml.widgets.group.Group
    enaml.widgets.v_group.VGroup
    enaml.widgets.h_group.HGroup
    enaml.widgets.form.Form
    enaml.widgets.group_box.GroupBox
    enaml.widgets.panel.Panel
    enaml.widgets.stacked_group.StackedGroup
    enaml.widgets.tab_group.TabGroup

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
    enaml.widgets.dialog.Dialog
    enaml.widgets.field.Field
    enaml.widgets.image.Image
    enaml.widgets.label.Label
    enaml.widgets.slider.Slider
    enaml.widgets.spin_box.SpinBox
    enaml.widgets.spacer.Spacer
    enaml.widgets.datetime_edit.DatetimeEdit
    enaml.widgets.date_edit.DateEdit

Special widgets
^^^^^^^^^^^^^^^

.. autosummary::
    :toctree: widgets
    :template: widget.rst

    enaml.widgets.html.Html
    enaml.widgets.traitsui_item.TraitsUIItem
    enaml.widgets.enable_canvas.EnableCanvas
    enaml.widgets.table_view.TableView
