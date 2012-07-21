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
    enaml.widgets.messenger_widget.MessengerWidget
    enaml.widgets.widget_component.WidgetComponent
    enaml.widgets.constraints_widget.ConstraintsWidget
    enaml.widgets.abstract_button.AbstractButton
    enaml.widgets.container.Container
    enaml.widgets.dialog.Dialog
    enaml.widgets.bounded_date.BoundedDate
    enaml.widgets.bounded_datetime.BoundedDatetime
    enaml.widgets.calendar.Calendar
    enaml.widgets.check_box.CheckBox
    enaml.widgets.combo_box.ComboBox
    enaml.widgets.date_edit.DateEdit
    enaml.widgets.datetime_edit.DatetimeEdit
    enaml.widgets.field.Field
    enaml.widgets.form.Form
    enaml.widgets.group_box.GroupBox
    enaml.widgets.html.Html
    enaml.widgets.image.Image
    enaml.widgets.image_view.ImageView
    enaml.widgets.label.Label
    enaml.widgets.notebook.Notebook
    enaml.widgets.page.Page
    enaml.widgets.progress_bar.ProgressBar
    enaml.widgets.push_button.PushButton
    enaml.widgets.radio_button.RadioButton
    enaml.widgets.scroll_area.ScrollArea
    enaml.widgets.slider.Slider
    enaml.widgets.spin_box.SpinBox
    enaml.widgets.text_editor.TextEditor
    enaml.widgets.window.Window
    :parts: 1


Standard Widgets
----------------

Abstract base widgets
^^^^^^^^^^^^^^^^^^^^^

.. autosummary::
    :toctree: widgets
    :template: widget.rst

    enaml.core.base_component.BaseComponent
    enaml.widgets.messenger_widget.MessengerWidget
    enaml.widgets.widget_component.WidgetComponent
    enaml.widgets.constraints_widget.ConstraintsWidget
    enaml.widgets.abstract_button.AbstractButton

Standard widgets
^^^^^^^^^^^^^^^^

.. autosummary::
    :toctree: widgets
    :template: widget.rst

    enaml.widgets.bounded_date.BoundedDate
    enaml.widgets.bounded_datetime.BoundedDatetime
    enaml.widgets.calendar.Calendar
    enaml.widgets.check_box.CheckBox
    enaml.widgets.combo_box.ComboBox
    enaml.widgets.date_edit.DateEdit
    enaml.widgets.datetime_edit.DatetimeEdit
    enaml.widgets.field.Field
    enaml.widgets.label.Label
    enaml.widgets.progress_bar.ProgressBar
    enaml.widgets.push_button.PushButton
    enaml.widgets.radio_button.RadioButton
    enaml.widgets.slider.Slider
    enaml.widgets.spin_box.SpinBox

Special widgets
^^^^^^^^^^^^^^^

.. autosummary::
    :toctree: widgets
    :template: widget.rst

    enaml.widgets.html.Html
    enaml.widgets.text_editor.TextEditor
    enaml.widgets.image_view.ImageView
    
Window widgets
^^^^^^^^^^^^^^^^^

.. autosummary::
    :toctree: widgets
    :template: widget.rst

    enaml.widgets.window.Window
    enaml.widgets.dialog.Dialog

Container and Layout widgets
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autosummary::
    :toctree: widgets
    :template: widget.rst

    enaml.widgets.container.Container
    enaml.widgets.form.Form
    enaml.widgets.group_box.GroupBox
    enaml.widgets.notebook.Notebook
    enaml.widgets.page.Page


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

Standard library
^^^^^^^^^^^^^^^^

A number of additional widget types are available in the standard widget
library.  These are not top-level classes implemented in Python, but are instead
|Enaml| widgets implemented using ``enamldef`` declarations.

.. toctree::
   :maxdepth: 2

    Standard Widget Library <std_library_ref>

