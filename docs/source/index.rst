.. traitsml documentation master file, created by
   sphinx-quickstart on Mon Aug 22 09:16:47 2011.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to TraitsML's documentation!
====================================

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


Prerequisites
-------------

- `Traits <https://github.com/enthought/traits>`_
- `PySide <http://www.pyside.org/>`_
- `PLY <http://www.dabeaz.com/ply/>`_ (Python Lex-Yacc),
  for parsing *.tml* files
- `Python <http://python.org/>`_ 2.6
- The "kitchen sink" example requires
  `Chaco <https://github.com/enthought/chaco>`



Contents:
---------

.. toctree::
   :maxdepth: 4

   tml
   traitsml
   developers_corner
