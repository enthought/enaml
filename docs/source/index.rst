.. enaml documentation master file

Welcome to enaml's documentation!
====================================

enaml is a tool for building native user interfaces on top of Traits. It
is a declarative language based on Python, analogous to Qt's QML. enaml
currently supports wxWidgets as a backend via wxPython and soon Qt as a
backend via PySide. However it is not tied to a single widget
toolkit.


.. warning:: Enaml is currently under heavy development and the
    documentation is not always up-to-date. Please recompile in order to
    have the latest changes from the source code.

Overview
========
An enaml application consists of regular Python code, and *.tml* files.

A .tml file is used to describe a GUI as a tree of elements. Each element
can have associated attributes, and an optional identifier. Attributes
customize the layout and behavior of an application, and identifiers allow
Python code to access widgets by name.

enaml parses a hierarchical .tml file, then renders it with an
available GUI toolkit. enaml abstracts away toolkit-specific details.

Other features:

- separation of presentation and content (i.e., MVC)
- a single script can work across multiple widget toolkits


Prerequisites
-------------

Enaml is developed using `Python <http://python.org/>`_ 2.7 and requires
recent versions of the following libraries:

- `Traits <https://github.com/enthought/traits>`_
- `PySide <http://www.pyside.org/>`_
- `wxPython <http://www.wxpython.org/>`_
- `PLY <http://www.dabeaz.com/ply/>`_ (Python Lex-Yacc),
  for parsing *.tml* files

Installation
------------



Contents
========

.. toctree::
    :maxdepth: 4

    tml
    developers_corner
