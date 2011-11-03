Writing .enaml Files
====================

Enaml files contain a domain-specific language for specifying a user-interface
and dynamically binding and computing values based on user interaction.

A simple example of an Enaml file might look something like this:

.. literalinclude:: examples/person_example.enaml
    :language: enaml

We could then use this with a Traits model as follows:

.. literalinclude:: examples/person_example.py
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

