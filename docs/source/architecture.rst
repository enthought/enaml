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
corresponding to each of the four different ways of using expressions: Defaults,
Binding, Notification and Delegation.

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
the top-level Window object as the view.

Finally the show() call on the Window recursively lays out the widgets and shows
them on the screen.
