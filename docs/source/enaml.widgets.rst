Widgets
=======

A widget in Enaml is a toolkit spesific implementation of an interface.
For each gui toolkit that is supported by Enaml a basic set of widgets
have been implemented and exist in the :mod:`enaml.widgets` submodule.

Interface
^^^^^^^^^

The interface describes the attributes and events that are exposed by the
enaml machinery and are available to the asossiated traits model to interact
with the graphics widget (i.e. the *view*).


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
    enaml.widgets.hgroup.HGroup
    enaml.widgets.html.Html
    enaml.widgets.window.Window
    enaml.widgets.vgroup.VGroup
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
    :parts: 1

Implementation
^^^^^^^^^^^^^^

For each interface there exists a traits object that implements the
required interface throught a very thin layer that wraps the tookit
specific widgets and exposes the necessary attributes. Value modifications
and events that take place during the life time of the graphic application
can be connected to our traits model by listing and updating the attributes
described in the interface.

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
    enaml.widgets.hgroup.IHGroupImpl
    enaml.widgets.html.IHtmlImpl
    enaml.widgets.window.IWindowImpl
    enaml.widgets.vgroup.IVGroupImpl
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
    enaml.widgets.vgroup.VGroup
    enaml.widgets.hgroup.HGroup
    enaml.widgets.form.Form
    enaml.widgets.group_box.GroupBox
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

Special widgets
^^^^^^^^^^^^^^^

.. autosummary::
    :toctree: widgets
    :template: widget.rst

    enaml.widgets.html.Html
    enaml.widgets.traitsui_item.TraitsUIItem
    enaml.widgets.enable_canvas.EnableCanvas
    enaml.widgets.table_view.TableView
