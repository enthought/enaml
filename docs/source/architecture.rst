Design and Architecture
=======================

Enaml is designed with a flexible, open architecture.  It is designed to be
able to adapt to different UI toolkit backends beyond the currently supported
Qt and Wx backends, as well as allowing other key parts of the infrastructure
to be replaced.

Construction of a View
^^^^^^^^^^^^^^^^^^^^^^

When building a view, you typically will create it via a sequence of commands
like::

    import enaml
    
    with enaml.imports():
        from my_view.enaml import MyView
    
    view = MyView(model)
    view.show()

The import step parses and compiles the Enaml file, creating a Python module
containing view factories that can be used by importing code.  When called,
these views factories expect model objects to be passed via arguments and then
use the UI toolkit to construct the actual UI components that will be used in
the view.  Finally the show() method starts the application mainloop if needed
and makes the UI components visible.

The enaml.imports() context manager provides an import hook that detects when an
``.enaml`` file is being imported parses it into an Enaml AST and uses
:py:class:`~enaml.enaml_compiler.EnamlCompiler` to compile it to Enaml bytecode.
From the importer's point of view it creates a standard Python module which has
one or more :py:class:`EnamlDefinition` objects which create
re-usable UI templates.  The :py:class:`EnamlDefinition` objects can be used by
other Enaml modules which import them, or directly by Python code.  Each
:py:class:`EnamlDefinition` instance is a namespace which can have additional
variable values supplied as arguments when it is called.

Calling an :py:class:`EnamlDefinition` object uses the supplied arguments to
build its namespace and then executes the Enaml bytecode to construct the UI
shell components.  The UI shell components are abstract objects which correspond
to Enaml components and which can use the provided toolkit to build the Enaml
toolkit widget tree.  Normally the toolkit to use is inferred from the environment
variables, but a particular toolkit can be selected with a with statement::

    from enaml.toolkit import wx_toolkit
    
    with wx_tookit():
        view = MyView(model)
    
    view.show()

Finally the show() call on the view object recursively creates the underlying
toolkit objects and goes through construction and initialization, calling each
Enaml Component's:

* ``create()`` method to create the toolkit object
* ``initialize()`` method to set the initial state of the toolkit object
* ``bind()`` method to bind event handlers (or the toolkit equivalents)

In addition, widgets which participate in constraints-based layout will have methods
called to register their constraints with the appropriate constraint solvers,
and then solve the layout.

Adding New Widgets
^^^^^^^^^^^^^^^^^^

These layers of abstraction and delegation mean that it is fairly simple to add
new widget types in custom applications.  To create a new widget, you need to:

    1)  Optionally, but ideally, define the abstract interface for your
        widget, which should be a subclass of the abstract base class
        :py:class:`~enaml.widgets.base_component.AbstractTkBaseComponent`
        be a subclass of :py:class:`~enaml.widgets.control.AbstractTkControl`.
        Since this is an abstract base class, you shouldn't implement any of the
        functionality in this class.

        This class provides the generic API the individual toolkit backends will
        need to implement, and will provide the methods that the Enaml widget
        will call.  In particular, there needs to be a specially named
        :py:meth:`shell_*_changed(self, value)` change handler for every
        dynamic Trait on the Enaml shell version of the Widget.

    2)  Create the Enaml shell version of the Widget.  This is a subclass of
        :py:class:`~enaml.widgets.base_component.BaseComponent`, and most likely a
        subclass of :py:class:`~enaml.widgets.control.Control`.  This class
        defines the interface that the Enaml markup language sees and can use.
        There should be, at a minimum, traits corresponding to values that can
        be read or changed on the widget, as well as methods for all standard
        actions that you want to give access to.

        This class is not abstract, and should provide all the functionality
        required in a toolkit-independent manner using the :py:attr:`toolkit_impl`
        implementation interface.  This must define a trait called
        :py:attr:`abstract_obj` which is an :py:class:`Instance()` of the
        implementation interface defined in the previous step.

    3)  Create a version of the Widget for each backend that you need to support.
        Each of these will be a subclass of the appropriate backend-specific
        component, such as :py:class:`~enaml.widgets.wx.wx_base_component.WXBaseComponent`
        or  :py:class:`~enaml.widgets.qt.qt_base_component.QtBaseComponent` as well as
        subclassing the abstract interface defined in the first step.  Once again,
        these are most likely to be subclasses of the appropriate Control classes.

        Instances of this class will have a :py:attr:`shell_obj` attribute
        which provides a reference to the Enaml shell widget instance for that
        control so that values can be obtained and inspected.

        This class must then, obviously, provide a concrete implemetation of the
        abstract interface.  In particular, it must provide the following methods
        (even if they are no-ops or implemented in a superclass):
        
            :py:meth:`create(self)`
                This is responsible for creating the underlying toolkit objects
                or widgets that the Enaml shell widget requires as part of its UI.

                You will almost always have to write this method.

            :py:meth:`initialize(self)`
                This is responsible for initializing the state of the toolkit
                object or objects based on the state of the Enaml shell widget.

                You will almost always have to write this method.

            :py:meth:`bind(self)`
                This is responsible for setting up the initial bindings of
                toolkit events to handlers on this object.

                You will almost always have to write this method.
        
        If you are writing a composite widget which contains a collection of
        toolkit widgets, as opposided to a single control-style widget, you
        may need to override the following:
        
            :py:meth:`size_hint(self)`
                This is responsible for returning a suggested size for the widget
                in its current state for use by the layout manager.
            
            :py:meth:`set_geometry(self, x, y, width, height)`
                This method is called when the layout system needs to re-position
                or resize the widget.  For a simple single widget control, this
                would usually just call the appropriate set geometry method on
                the underlying toolkit widget, but for an Enaml widget composed
                of multiple toolkit widgets you will need to lay them out
                relative to each other and the space that they have been provided.
        
        In addition to these standard methods, you will need to provide
        implementations for each of the methods you declared in the first step:

            :py:meth:`shell_*_changed(self, value)`
                This has to react to a change to the appropriate trait on the
                Enaml widget and change the appropriate toolkit state.

        as well as any other methods.

.. warning:: These methods are outdated

        To handle styling

            :py:meth:`create_style_handler(self)`
                This is responsible for creating a :py:class:`StyleHandler`
                instance.  You may need to implement a custom subclass of
                :py:class:`StyleHandler` if your widget has unusual styling
                needs.

                If your styling needs are simple, you may be able to
                define an appropriate :py:attr:`tags` class attribute which
                maps supported style tags to toolkit-dependent information,
                and use the default implementation of the method from the
                toolkit.

            :py:meth:`initialize_style(self)`
                This method is responsible for initializing the values on the
                :py:class:`StyleHandler` class created by the previous method.

                If your styling needs are simple, you may be able to use the
                default toolkit implementation of this class.

            :py:meth:`layout_child_widgets(self)`
                This method is used by :py:class:`Container` implementations to
                insert child widgets into the appropriate toolkit-specific
                layout object, and set the appropriate attributes and properties
                of this object.  Most simple Control subclasses do not need to
                implement this, since they do not have child widgets.

    4)  Create the toolkit constructor and add it to the appropriate toolkit
        object.  There are several ways to do this, depending on your goals:
        
            *   if you are adding a new control type to the main Enaml source,
                then you can directly create a constructor in the toolkit's
                ``constructors.py`` module.  This module contains a dictionary
                of constructors and a utility function for building them
                assuming that you have followed a naming pattern for your classes
                which is consistent with the rest of the toolkit widgets.
                
                Typically this will look something like::
                
                    QT_CONSTRUCTORS = dict((
                        ...
                        constructor('my_new_widget'),
                    ))
            
            *   if you are adding a new control type that is specific to your
                code and not part of the main Enaml system, then you will need
                to manually create an :py:class:`~enaml.toolkit.Constructor`
                instance and add it to an appropriate toolkit.  Building a
                constructor is simply a matter of creating a new
                :py:class:`~enaml.toolkit.Constructor` with your Enaml shell
                class from step (2) and your toolkit backend class from step (3).
                
                Typical code for this would look like::
                
                    from enaml.toolkit import Constructor
                    
                    from my_widgets.my_new_widgets import MyNewWidget
                    from my_widgets.qt.qt_my_new_widgets import QtMyNewWidget
                
                    ctor = Constructor(MyNewWidget, QtMyNewWidget)
                    
                Once you have the constructor you need to add it to a toolkit.
                If you want this to be globally available in your process as part
                of the appropriate toolkit then you need to add it to the toolkit's
                constructor dictionary before you create any views::
                
                    from enaml.widgets.qt.constructors import QT_CONSTRUCTORS
                    
                    QT_CONSTRUCTORS['MyNewWidget'] = ctor
                    
                Any subsequent calls to :py:func:`~enaml.toolkit.qt_toolkit` will
                now contain your new widget.
                
                Alternatively, you may want to create your own toolkit that is
                separate from the usual backend toolkit::
                
                    from enaml.toolkit import qt_toolkit
                    
                    my_toolkit = qt_toolkit()
                    my_toolkit['MyNewWidget'] = ctor
                
                This will create a new toolkit which has all of the widgets in
                the standard Qt toolkit, but also includes yours.  Code can then
                choose whether to use the standard Qt toolkit or your new toolkit
                as appropriate.
        
.. warning:: These sections are outdated

Implementing A New Toolkit
^^^^^^^^^^^^^^^^^^^^^^^^^^

Currently Enaml supports the Qt toolkit and the Wx toolkit (on Windows only).
The architecture is designed to be as toolkit-independent as possible.  To
implement a new architecture, you will need to perform the following steps:

    1)  Create a constructor objects for the standard Enaml widgets for your
        toolkit.  Look at the Wx and Qt toolkit's constructor modules to see
        how to go about this in detail, but you will need to implement subclasses
        of :py:class:`enaml.constructor.BaseToolkitCtor` for each of the widget
        types.  You will probably want to define base constructors for
        simple :py:class:`Component`, :py:class:`Window`, :py:class:`Panel`,
        and :py:class:`Container` instances.

        The :py:class:`Container` base constructor should define a
        :py:meth:`construct()` method which should call the constructor of all
        of the children of the container.  Other classes may want to handle
        embedding the widget in a top-level Window, or ensuring that children
        are embedded in a panel.

        All of the non-base constructors should implement a :py:meth:`component()`
        method that imports the Enaml widget class and the toolkit implementation
        class and creates the objects as described in the previous section's
        discussion of toolkit constructors.

    2)  Create a default stylesheet for your toolkit.  Initially it may be
        sufficient to copy the stylesheet for an existing backend, since the
        stylesheet definitions are toolkit-independent.

    3)  Create a new toolkit factory for your new backend.  This should look
        something like the current :py:class:`enaml.toolkit.wx_toolkit` or
        :py:class:`enaml.toolkit.qt_toolkit` factories.  This toolkit object
        needs to be supplied with:

            :py:func:`prime()`
                A function that is responsible for obtaining (or creating, if it
                doesn't yet exist) the main toolkit application object, or
                otherwise performing whatever initialization is needed to allow
                widgets to be created.  It should not start the main event loop,
                however.

                This should return the application object, if appropriate.

            :py:func:`start(app)`
                A function that takes an application object returned by
                :py:func:`prime()` and starts the main event loop.

            :py:attr:`items`
                A dictionary mapping Enaml entity names to toolkit constructors
                classes for each available widget type.

            :py:attr:`style_sheet`
                The default stylesheet for your toolkit.

            :py:attr:`utils`
                A dictionary of utility functions to be addd to the Enaml
                namspace.  This will eventually include the standard toolkit
                dialog implementations.

    4)  Write toolkit-specific implementations of each Enaml widget.  See the
        previous section for discussion for the methods that you will need to
        implement on this class.

        This is where the bulk of the work will be performed.

    5)  Write the implementations of auxilliary objects, such as dialog windows.

If all of the above steps are performed correctly, you should be able to display
any Enaml UI in your new toolkit.


Using A Different Notification Model
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Enaml uses Enthought's Traits system by default for handling binding and
notification of expressions to model attributes.  You may have existing code
which uses a different system for reacting to changes within the model, and
Enaml can be extended to be able to use these systems as well.  This would
allow developers to write code which might do things like access a model on
a remote machine, or stored in a database.

To support this sort of behaviour, you will probably want to have a base class
that all model objects with this new reaction mechanism inherit from, or some
other simple way that these model instances can be distinguished from regular
Python or Traits instances.

You may then need to implement subclasses of
:py:class:`enaml.expressions.DefaultExpression`,
:py:class:`enaml.expressions.BindingExpression`,
:py:class:`enaml.expressions.DelegateExpression`,  and
:py:class:`enaml.expressions.NotifierExpression` that correctly handle these
interactions.  When implementing overriden methods, all of these subclasses
must check to see whether the model object is of the new model type, and if
it is not then they need to use the standard superclass implementation of the
method.  If this is not done then expressions involving widget traits will
fail to work correctly.

    :py:class:`~enaml.expressions.DefaultExpression`
        This class needs to be able to provide a default value for the
        expression, but does not need to react to changes in the model object
        or in the Enaml namespace.

        You may need to override the :py:meth:`__value_default()` handler
        to compute the default value from the model, but ideally you should
        be able to use this class unmodified.

    :py:class:`~enaml.expressions.BindingExpression`
        This class needs to provide a default value for the expression, but
        also needs to analyze the expression for dependencies and react to
        changes in the dependency values.

        You may need to override the :py:meth:`__value_default()` handler
        to as in the :py:class:`~enaml.expressions.DefaultExpression` case.

        You will also need to override the :py:meth:`bind()` method to correctly
        hook up the expression to its dependencies in your model's notification
        model.  For example, you may have to register a callback with an
        appropriate object.  This callback will probably look something
        like the :py:meth:`refresh_value()` method, but may need to perform
        additional steps depending on your model.

    :py:class:`~enaml.expressions.NotifierExpression`
        This class requires the ability to execute a code expression whenever
        an Enaml attribute changes.

        You may need to override the :py:meth:`notify()` method to compute the
        expression correctly, but ideally you should be able to use this
        class unmodified.

    :py:class:`~enaml.expressions.DelegateExpression`
        This class requires both the ability to analyze and react to changes
        in expression dependencies, but also push changes from the Enaml
        trait which it is connected to onto the designated object.

        This will require an appropriate :py:meth:`bind()` method similar to
        the one that the :py:class:`~enaml.expressions.BindingExpression` uses,
        although the allowable expressions are much simpler for
        :py:class:`~enaml.expressions.DelegateExpression`.

        You will also need to override the implementations of
        :py:meth:`_get_value()` and :py:meth:`_set_value()` to appropriately
        change the value on the underlying model.

Having written these classes, you will need to define
:py:class:`BaseExpressionFactory` subclasses for each class and have the
:py:meth:`__call__` methods construct the appropriate expression instance.

Finally you will need to subclass :py:class:`EnamlFactory` and override the
:py:meth:`expression_factories` method to return the new expression factory
classes.
