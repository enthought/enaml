Widgets
===============================================================================

An Enaml widget is a toolkit-independent abstraction.
Each GUI toolkit that Enaml supports is a set of widgets that
have been implemented and exist in the :mod:`enaml.components` submodule.
A widget interface is not tied to any particular implementation.

Interface
---------

An Enaml widget's interface describes the attributes and events that the
widget exposes as its API. Enaml orchestrates communication between
user-facing views and the underlying graphical toolkits.

*Standard interfaces*

.. inheritance-diagram::
    enaml.core.base_component.BaseComponent
    enaml.components.abstract_item_view.AbstractItemView
    enaml.components.action.Action
    enaml.components.base_selection_model.BaseSelectionModel
    enaml.components.row_selection_model.RowSelectionModel
    enaml.components.base_widget_component.BaseWidgetComponent
    enaml.components.bounded_date.BoundedDate
    enaml.components.bounded_datetime.BoundedDatetime
    enaml.components.calendar.Calendar
    enaml.components.check_box.CheckBox
    enaml.components.combo_box.ComboBox
    enaml.components.constraints_widget.ConstraintsWidget
    enaml.components.control.Control
    enaml.components.date_edit.DateEdit
    enaml.components.datetime_edit.DatetimeEdit
    enaml.components.enable_canvas.EnableCanvas
    enaml.components.field.Field
    enaml.components.float_slider.FloatSlider
    enaml.components.html.Html
    enaml.components.image_view.ImageView
    enaml.components.label.Label
    enaml.components.list_view.ListView
    enaml.components.progress_bar.ProgressBar
    enaml.components.push_button.PushButton
    enaml.components.radio_button.RadioButton
    enaml.components.slider.Slider
    enaml.components.spin_box.SpinBox
    enaml.components.table_view.TableView
    enaml.components.text_editor.TextEditor
    enaml.components.toggle_button.ToggleButton
    enaml.components.toggle_control.ToggleControl
    enaml.components.traitsui_item.TraitsUIItem
    enaml.components.tree_view.TreeView
    enaml.components.container.Container
    enaml.components.form.Form
    enaml.components.group_box.GroupBox
    enaml.components.tab.Tab
    enaml.components.scroll_area.ScrollArea
    enaml.components.splitter.Splitter
    enaml.components.tab_group.TabGroup
    enaml.components.menu.Menu
    enaml.components.menu_bar.MenuBar
    enaml.components.dock_pane.DockPane
    enaml.components.window.Window
    enaml.components.main_window.MainWindow
    enaml.components.dialog.Dialog
    enaml.components.directory_dialog.DirectoryDialog
    enaml.components.file_dialog.FileDialog
    enaml.components.include.Include
    enaml.components.inline.Inline
    :parts: 1

Implementation
--------------

The available backends provide concrete versions of Enaml widget
interfaces. An interface utilizes an implementation-specific
class, which wraps an actual toolkit widget.


*Standard Implementations*

.. inheritance-diagram::
    enaml.components.abstract_application.AbstractTkApplication
    enaml.components.abstract_item_view.AbstractTkItemView
    enaml.components.action.AbstractTkAction
    enaml.components.base_selection_model.AbstractTkBaseSelectionModel
    enaml.components.base_widget_component.AbstractTkBaseWidgetComponent
    enaml.components.bounded_date.AbstractTkBoundedDate
    enaml.components.bounded_datetime.AbstractTkBoundedDatetime
    enaml.components.calendar.AbstractTkCalendar
    enaml.components.check_box.AbstractTkCheckBox
    enaml.components.combo_box.AbstractTkComboBox
    enaml.components.constraints_widget.AbstractTkConstraintsWidget
    enaml.components.control.AbstractTkControl
    enaml.components.date_edit.AbstractTkDateEdit
    enaml.components.datetime_edit.AbstractTkDatetimeEdit
    enaml.components.enable_canvas.AbstractTkEnableCanvas
    enaml.components.field.AbstractTkField
    enaml.components.float_slider.AbstractTkFloatSlider
    enaml.components.html.AbstractTkHtml
    enaml.components.image_view.AbstractTkImageView
    enaml.components.label.AbstractTkLabel
    enaml.components.list_view.AbstractTkListView
    enaml.components.progress_bar.AbstractTkProgressBar
    enaml.components.push_button.AbstractTkPushButton
    enaml.components.radio_button.AbstractTkRadioButton
    enaml.components.slider.AbstractTkSlider
    enaml.components.spin_box.AbstractTkSpinBox
    enaml.components.table_view.AbstractTkTableView
    enaml.components.text_editor.AbstractTkTextEditor
    enaml.components.toggle_button.AbstractTkToggleButton
    enaml.components.toggle_control.AbstractTkToggleControl
    enaml.components.traitsui_item.AbstractTkTraitsUIItem
    enaml.components.tree_view.AbstractTkTreeView
    enaml.components.container.AbstractTkContainer
    enaml.components.form.AbstractTkForm
    enaml.components.group_box.AbstractTkGroupBox
    enaml.components.tab.AbstractTkTab
    enaml.components.scroll_area.AbstractTkScrollArea
    enaml.components.splitter.AbstractTkSplitter
    enaml.components.tab_group.AbstractTkTabGroup
    enaml.components.dock_pane.AbstractTkDockPane
    enaml.components.window.AbstractTkWindow
    enaml.components.dialog.AbstractTkDialog
    enaml.components.main_window.AbstractTkMainWindow
    enaml.components.directory_dialog.AbstractTkDirectoryDialog
    enaml.components.file_dialog.AbstractTkFileDialog
    :parts: 1

Standard Widgets
----------------

Abstract base widgets
^^^^^^^^^^^^^^^^^^^^^

.. autosummary::
    :toctree: widgets
    :template: widget.rst

    enaml.core.base_component.BaseComponent
    enaml.components.base_widget_component.BaseWidgetComponent
    enaml.components.widget_component.WidgetComponent
    enaml.components.constraints_widget.ConstraintsWidget
    enaml.components.layout_task_handler.LayoutTaskHandler
    enaml.components.control.Control
    enaml.components.toggle_control.ToggleControl
    enaml.components.bounded_date.BoundedDate
    enaml.components.abstract_item_view.AbstractItemView
    enaml.components.base_selection_model.BaseSelectionModel

Standard control widgets
^^^^^^^^^^^^^^^^^^^^^^^^

.. autosummary::
    :toctree: widgets
    :template: widget.rst

    enaml.components.calendar.Calendar
    enaml.components.check_box.CheckBox
    enaml.components.combo_box.ComboBox
    enaml.components.push_button.PushButton
    enaml.components.radio_button.RadioButton
    enaml.components.field.Field
    enaml.components.image.Image
    enaml.components.label.Label
    enaml.components.slider.Slider
    enaml.components.spin_box.SpinBox
    enaml.components.datetime_edit.DatetimeEdit
    enaml.components.date_edit.DateEdit
    enaml.components.progress_bar.ProgressBar

Special widgets
^^^^^^^^^^^^^^^

.. autosummary::
    :toctree: widgets
    :template: widget.rst

    enaml.components.html.Html
    enaml.components.text_editor.TextEditor
    enaml.components.image_view.ImageView
    enaml.components.traitsui_item.TraitsUIItem
    enaml.components.enable_canvas.EnableCanvas
    
Window widgets
^^^^^^^^^^^^^^^^^

.. autosummary::
    :toctree: widgets
    :template: widget.rst

    enaml.components.window.Window
    enaml.components.main_window.MainWindow
    enaml.components.dialog.Dialog
    enaml.components.directory_dialog.DirectoryDialog
    enaml.components.file_dialog.FileDialog

Container and Layout widgets
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autosummary::
    :toctree: widgets
    :template: widget.rst

    enaml.components.container.Container
    enaml.components.form.Form
    enaml.components.group_box.GroupBox
    enaml.components.tab.Tab
    enaml.components.splitter.Splitter
    enaml.components.scroll_area.ScrollArea
    enaml.components.tab_group.TabGroup
    enaml.components.dock_pane.DockPane


Item views
^^^^^^^^^^

.. autosummary::
    :toctree: widgets
    :template: widget.rst

    enaml.components.list_view.ListView
    enaml.components.table_view.TableView
    enaml.components.tree_view.TreeView

Menu widgets
^^^^^^^^^^^^

.. autosummary::
    :toctree: widgets
    :template: widget.rst

    enaml.components.menu_bar.MenuBar
    enaml.components.menu.Menu

