========
TraitsML
========

TraitsML is a tool for building native user interfaces on top of Traits.
It is a declarative language based on Python, analogous to Qt's QML.
TraitsML currently supports Qt as a backend via PySide,
but it is not tied to a single widget toolkit. 


Overview
========
A TraitsML application consists of regular Python code, and *.tml* files.

A .tml file is used to describe a GUI as a tree of elements.
Each element can have associated attributes, and an optional identifier.
Attributes customize the layout and behavior of an application, and
identifiers allow Python code to access widgets by name.

TraitsML parses a hierarchical .tml file, then renders it with an
available GUI toolkit. TraitsML abstracts away toolkit-specific details.

Other features:

- separation of presentation and content (i.e., MVC)
- a single script can work across multiple widget toolkits


Writing .tml Files 
==================

Binding Operators
-----------------

`=`
  *Assignment*. RHS can be any expression. The assignment will 
  be the default value, but the value can be changed later
  through Python code or TML expression execution.

`~~`  
  *Delegation*. RHS must be a simple attribute expression, 
  like a.b or a.b.c and so on. Non-attribute expressions here
  are a syntax error. The value of the view property and value
  of the attribute are synced, but the type checking of the
  view property is enforced.

`<<`
  *Binding*. RHS can be any expression. The expression will be 
  parsed for dependencies, and any dependency which is a trait
  attribute on a HasTraits class will have a listener attached.
  When the listener fires, the expression will be re-evaluated
  and the value of the view property will be updated.

`>>` 
  *Notification*. RHS can be any expression. The expression will
  be evaluated any time the view property changes.


Scoping Rules
-------------

- Imports are global and accessible to everything in the file.
- Each top-level item defines its own global namespace, which is
  unioned with the imports. This namespace includes all elements
  that have a declared identifier.
- Each item has a local namespace that includes `self` and `parent`. 
  The `self` is a reference to the element itself, whether anonymous
  or not. The `parent` is a reference to this item's parent element,
  whether anonymous or not. The `parent` of top-level elements
  is None.


Prerequisites
=============
- `Traits <https://github.com/enthought/traits>`_
- `PySide <http://www.pyside.org/>`_
- `PLY <http://www.dabeaz.com/ply/>`_ (Python Lex-Yacc),
  for parsing *.tml* files
- `Python <http://python.org/>`_ 2.6
- The "kitchen sink" example requires 
  `Chaco <https://github.com/enthought/chaco>`

