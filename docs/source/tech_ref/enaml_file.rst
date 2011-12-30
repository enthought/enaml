Writing .enaml Files
====================

Enaml files contain a domain-specific language for specifying a user-interface
and dynamically binding and computing values based on user interaction.

A simple example of an Enaml file might look something like this:

.. literalinclude:: ../examples/person_example.enaml
    :language: python

We could then use this with a Traits model as follows:

.. literalinclude:: ../examples/person_example.py
    :language: python

Looking at this example, you will see that an Enaml file consists of one or
more ``defn`` blocks containing a widget tree that describes the layout of
that part of the UI.  The widgets have attributes which are bound to expressions
in various ways, allowing simple reactivity.  Widgets can be assigned names using
the ``->`` operator and then their attributes are available to other parts of
the UI.

On the Python side, the Enaml code can be imported using a ``with`` statement
to add the Enaml import hooks.  The ``defn`` blocks are then available as
module-level functions that can be called normally from Python code.  Building
the UI is then a matter of calling an Enaml ``defn`` to build the view, and then
calling ``show()`` on the view to display it and start the application event loop.
The parameters passed in to the Enaml ``defn`` block from the Python side can be
any Python or Enaml objects that would make sense to use within the Enaml code.
For example, if you use an attribute of an object in the Enaml code, then passing
an object without that attribute will raise an ``AttributeError`` just as if you
did the same thing in a Python function.

Enaml Components and Layout
---------------------------

Enaml widgets come in two basic types: Containers and Controls.  Controls
are conceptually single UI elements with no other Enaml widgets inside them,
such as labels, fields, and buttons.  Containers are widgets which contain other
widgets, usually including information about how to layout the widgets that they
contain.  Examples of containers include top-level windows, dialogs and forms.

Enaml uses constraints-based layout implemented by the Cassowary layout system.
Constraints are specified as a system of linear inequalities together with an
error function which is minimized according to a modified version of the Simplex
method.  The error function is specified via assigning weights to the various
inequalities.  The default weights exposed in Enaml are ``'weak'``, ``'strong'``
and ``'required'``, but other values are possible within the system, if needed.
While a developer writing Enaml code could specify all constraints
directly, in practice they will use a set of helper classes, functions and
attributes to help specify the set of constraints in a more understandable way.

Every widget knows its preferred size, usually by querying the underlying toolkit,
and can express how closely it adheres to the preferred size via its ``hug__width``,
``hug_height``, ``resist_clip_width`` and ``resist_clip_height`` which take the
a weight or ``'ignore'``.  These are set to reasonable defaults for most widgets,
but they can be overriden. The ``hug`` attributes specify how strongly the widget
resists expansion by adding a constraint of the appropriate weight that specifies
that the dimension be equal to the preferred value, while the ``resist_clip``
attributes specify how strongly the widget resists compression by adding a constraint
that specifies that the dimension be greater than or equal to the preferred value.

XXX Example here

Containers can specify additional constraints that relate their child widgets.
By default a container simply lays out its children as a vertical list and tries
to expand them to use the full width and height that the container has available.
Layout containers, like Form, specify different default constraints that give
automatic layout of their children, and may provide additional hooks for other
widgets to use to align with their significant features.

Additional constraints are specified via the ``constraints`` attribute on the
container.  The simplest way to specify a constraint is with a simple equality
or inequality.  Inequalities can be specified in terms of symbols provided
by the components, which at least default to the box model's symbols: ``top``,
``bottom``, ``left``, ``right``, ``v_center``, ``h_center``, ``width`` and
``height``.  Other components may expose other symbols: for example the Form
widget exposes ``midline`` for aligning the fields of multiple forms along
the same line.

XXX Example here

However, this can get tedious, and so there are some helpers that are
available to simply specifying layout.  These are:

    ``_space_``
        A singleton spacer that represents a flexible space in a layout
        with a minimum value of the default space.  Additional restrictions
        on the space can be specified using ``==``, ``<=`` and ``>=`` with
        an integer value.

    ``horizontal(*items)``

    ``vertical(*items)``
        These two functions take a list of symbols, widgets and spacers and
        create a series of constraints that specify a sequential horizontal
        or vertical layout where the sides of each object in sequence abut
        against each other.

    ``align_left(*items)``

    ``align_right(*items)``

    ``align_top(*items)``

    ``align_bottom(*items)``

    ``align_v_center(*items)``

    ``align_h_center(*items)``
        These functions take a list of widgets and align the appropriate
        parts of their box models.

By using appropriate combinations of these objects you can specify complex layouts
quickly and clearly.

XXX Example here

Binding Operators
-----------------

`=`
  *Assignment*. RHS can be any expression. The assignment will be the
  default value, but the value can be changed later through Python code or
  expression execution.

`:=`
  *Delegation*. RHS must be a simple attribute expression, like foo.bar .
  Non-attribute expressions here are a runtime error. The value of the
  view property and value of the attribute are synced, but the type
  checking of the view property is enforced.

`<<`
  *Binding*. RHS can be any expression. The expression will be parsed for
  dependencies, and any dependency which is a trait attribute on a
  HasTraits class will have a listener attached. When the listener fires,
  the expression will be re-evaluated and the value of the view property
  will be updated.

`>>`
  *Notification*. RHS can be any expression. The expression will be
  evaluated any time the view property changes.


Scoping Rules
-------------

- Imports are global and accessible to everything in the file.
- Each top-level item defines its own local namespace. This namespace
  includes all elements that have a declared identifier.
- Each expression has its local namespace that is the union of the block
  locals and the attribute namespace of the object to which the expression
  is bound. In otherwords `self` is implicit. However, a `self` exists in
  this local namespace in order to break naming conflicts between block
  locals and attribute names. To any C++ or Java developers, this will seem
  natural.

