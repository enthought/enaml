Design and Architecture
=======================

.. warning:: This sections is outdated

Enaml is designed with a flexible, open architecture.  It is designed to be
able to adapt to different UI toolkit backends beyond the currently supported
Qt and Wx backends, as well as allowing other key parts of the infrastructure
to be replaced.

Construction of a View
^^^^^^^^^^^^^^^^^^^^^^

When building a view, you typically will create it via a sequence of commands
like::

    factory = EnamlFactory('my_view.enaml')
    view = factory(model=my_model, table_model=my_table)
    view.show()

These steps create a view factory, prime its namespace with model objects from
your application that correspond to the unspecified names in the .enaml file,
and the display the window.

The first call, to :py:class:`~enaml.factory.EnamlFactory(file, toolkit)`,
loads the ``.enaml`` file and parses it into an abstract syntax tree (AST).
An optional argument here can set the back-end toolkit to be used, and if
nothing is specified will use the default toolkit defined in
:py:mod:`enaml.toolkit`.  At this point no actual objects are constructed
representing the elements of the view in the ``.enaml`` file.

When the resulting factory object is called the factory first builds a tree
of widget constructors for each widget in the ``.enaml`` file, and creates
binding information for the expressions.  The widget constructors are instances
of subclasses of :py:class:`BaseToolkitCtor` that are obtained from the toolkit
object.  Expressions bindings are represented by suclasses of :py:class:`BaseExpression`
corresponding to each of the four different ways of using expressions: Default,
Binding, Notification and Delegation.  This tree is built just once for each
factory instance, so subsequent calls to the factory with different namespace
arguments will not repeat this work.

The factory then builds the namespace for the view, and primes the toolkit
(this usually creates a toolkit application object if one does not already exist).
Finally, the factory calls the root of the constructor tree with the view's
namespace, and this then walks the tree building the UI and connecting the
objects in the namespace to the expression bindings.  Each widget in the UI
has two objects: a subclass of :py:class:`Component` which is responsible
for handling expression binding and the Enaml side of the widget tree, and
a subclass of the toolkit's component representation (eg. :py:class:`WXComponent`
or :py:class:`QtComponent`) which holds the reference to the actual toolkit
objects that are created and handles the toolkit-specific aspects of widget
creation, layout, styling and interaction.  The factory call then returns
a View object that contains the top-level Window object and a namespace proxy.

Finally the show() call on the Window recursively lays out the widgets, sets
styles and shows them on the screen.

The factory can be re-called with different arguments to create different views
using the same Enaml specification.

Adding New Widgets
^^^^^^^^^^^^^^^^^^

These layers of abstraction and delegation mean that it is fairly simple to add
new widget types in custom applications.  To create a new widget, you need to:

    1)  Optionally, but ideally, define the implementation interface for your
        widget, which should be a subclass of
        :py:class:`~enaml.widgets.component.IComponentImpl`, and probably will
        be a subclass of :py:class:`~enaml.widgets.control.IControlImpl`. Since
        this is an interface definition, you shouldn't implement any of the
        functionality in this class.

        This class provides the generic API the individual toolkit backends will
        need to implement, and will provide the methods that the Enaml widget
        will call.  In particular, there needs to be a specially named
        :py:meth:`parent_*_changed(self, value)` change handler for every
        dynamic Trait on the Enaml version of the Widget.

    2)  Create the Enaml version of the Widget.  This is a subclass of
        :py:class:`~enaml.widgets.component.Component`, and most likely a
        subclass of :py:class:`~enaml.widgets.control.Control`.  This class
        defines the interface that the Enaml markup language sees and can use.
        There should be, at a minimum, traits corresponding to values that can
        be read or changed on the widget, as well as methods for all standard
        actions that you want to give access to.

        These classes must define a trait called :py:attr:`toolkit_impl` which
        is an :py:class:`Instance()` of the implementation interface defined
        above.  This class is not abstract, and should provide all the
        functionality required in a toolkit-independent manner using the
        :py:attr:`toolkit_impl` implementation interface.

    3)  Create a version of the Widget for each backend that you need to support.
        Each of these will be a subclass of the appropriate backend-specific
        component, such as :py:class:`~enaml.widgets.wx.wx_component.WXComponent`
        or  :py:class:`~enaml.widgets.qt.qt_component.QtComponent`.  Once again,
        these are most likely to be subclasses of the appropriate Control classes.

        This class must claim that it implements the appropriate implementation
        interface defined in the first step, eg.::

            from traits.api import implements

            class QtMyControl(QtControl):
                """My new custom control."""
                implements(IMyControlImpl)
                ...

        This instances of this class will have a :py:attr:`parent` attribute
        which provides a reference to the Enaml widget instance that control
        so that values can be obtained and inspected.

        This class must then, obviously, provide a concrete implemetation of the
        abstract interface.  In particular, it must provide the following methods
        (even if they are no-ops or implemented in a superclass):

            :py:meth:`create_widget(self)`
                This is responsible for creating the underlying toolkit widget
                or widgets that the Enaml widget requires.

                You will almost always have to write this method.

            :py:meth:`initialize_widget(self)`
                This is responsible for initializing the state of the toolkit
                widget based on the state of the Enaml widget :py:attr:`widget`.

                You will almost always have to write this method.

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

        In addition to these standard methods, you will need to provide
        implementations for each of the methods you declared in the first step:

            :py:meth:`parent_*_changed(self, value)`
                This has to react to a change to the appropriate trait on the
                Enaml widget and change the appropriate toolkit state.

        as well as any other methods.

    4)  Create the toolkit constructor.  You need to create a constructor class
        which knows how to create the appropriate Enaml and toolkit versions of
        the widget and link them together.  A typical implementation will look
        something like::

            class QtMyControlCtor(QtBaseComponentCtor):
                implements(IToolkitConstructor)

                def component(self):
                    from ..my_control import MyControl
                    from .qt_my_control import QtMyControl
                    my_control = MyControl(toolkit_impl=QtMyControl())
                    return my_control

        You will need one of these for each toolkit that you support.

    5)  Add the constructor to the toolkit object.  To be able to use the new
        widget from Enaml files, you need to insert it into the toolkit that you
        are going to use with yout Enaml file.  There are several different ways
        to perform this action:

            *   You can create a special-purpose toolkit instance and modify
                its :py:attr:`items` dictionary::

                    my_qt_toolkit = qt_toolkit()
                    my_qt_toolkit.items['MyControl'] = QtMyControlCtor

                This can be done in an ad-hoc fashion immediately before
                creating your EnamlFactory instance and passed in as the
                second argument to its constructor::

                    factory = EnamlFactory(my_file, my_qt_toolkit)

            *   You can write your own special-purpose toolkit factory that
                creates an instance of :py:class:`enaml.toolkit.Toolkit`.  This
                could be something as simple as::

                    def my_qt_toolkit():
                        toolkit = qt_toolkit()
                        toolkit.items['MyControl'] = QtMyControlCtor
                        return toolkit

                You can then use this in the EnamlFactory::

                    factory = EnamlFactory(my_file, my_qt_toolkit())

                This is probably the preferred approach if you are adding
                multiple new controls or want to use the new widget in multiple
                Enaml files.

            *   If you are adding controls to the main Enaml source, then you
                can add your new constructors to the backend-specific toolkit
                factories by editing :py:mod:`enaml.toolkit` directly.

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
