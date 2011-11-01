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

