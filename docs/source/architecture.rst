Design and Architecture
-----------------------

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
