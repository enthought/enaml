.. enaml documentation master file

Welcome to enaml's documentation!
====================================

**E**\naml is **N**\ot **A** **M**\arkup **L**\anguage, is a tool for building
native user interfaces on top of Traits. It is a declarative language
based on Python, analogous to Qt's QML. enaml currently supports wxWidgets
as a backend via wxPython and Qt as a backend via PySide. However it is
not tied to a single widget toolkit.

.. warning:: Enaml is currently under heavy development and the
    documentation is not always up-to-date. Please recompile in order to
    have the latest changes from the source code.

Overview
--------
An enaml application consists of regular Python code, and *.tml* files.

A .enaml file is used to describe a GUI as a tree of elements. Each element
can associated attributes, and an optional identifier. Attributes
customize the layout and behaviour of an application, and identifiers allow
Python code to access widgets by name.

enaml parses a hierarchical file (.enaml), then renders it with an
available GUI toolkit. Enaml abstracts away toolkit-specific details.


Goals
^^^^^

The goals of the enaml project is to:

- Intergrate well with `Traits <https://github.com/enthought/traits>`_ and
  `Chaco <http://code.enthought.com/chaco/>`_ .
- Help **separate** the presentation and content (i.e., MVC)
- A **single** script can work across *multiple* widget toolkits when
  using the default interfaces.
- Easily **extensible** to accomodate adaptation and addition of the base
  widgets.

Prerequisites
^^^^^^^^^^^^^

Enaml is developed using `Python <http://python.org/>`_ 2.7 and requires
recent versions of the following libraries:

*Required*:

- `Traits <https://github.com/enthought/traits>`_
- `PySide <http://www.pyside.org/>`_
- `wxPython <http://www.wxpython.org/>`_ with a recent (> 0.9.1)
  `agw <http://xoomer.virgilio.it/infinity77/AGW_Docs/index.html>`_
  library
- `PLY <http://www.dabeaz.com/ply/>`_ (Python Lex-Yacc),
  for parsing *.enaml* files
- `distribute <http://pypi.python.org/pypi/distribute>`_ (package
  installation)

*Optional*:

- `Graphviz <http://www.graphviz.org/>`_ (used for documention)


Installation
^^^^^^^^^^^^

To install the package please check out the source from
`github <https://github.com/enthought/enaml>`_ execute::

    python setup.py install

Alternatively you can work in developing mode with::

    python setup.py develop

|

To test the package just execute::

    python setup.py test

.. note:: Currently the test coverage of the project is relativly low. Also
    due to the fast development paces tests become often obsolute and fail
    because the overall arhitecture has changed.


Example
^^^^^^^

For the impatient enaml user here an example::

    enaml code

An the python script to execute it::

    python code

Results in the following widget




Contents
--------

.. toctree::
    :maxdepth: 2

    Examples
    enaml_file
    Library Reference <modules>
    developers_corner
