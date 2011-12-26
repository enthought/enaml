Overview
--------
An |Enaml| application consists of regular Python code, and *.enaml* files.

A .enaml file describes a GUI as a tree of elements. Each element has
associated attributes and an optional identifier. **Attributes** customize the
layout and behaviour of an application, and **identifiers** allow Python code
to access widgets by name.

|Enaml| parses a hierarchical file (.enaml), then renders it with an
available GUI toolkit. |Enaml| abstracts away toolkit-specific details.


Goals
^^^^^

The goals of the |Enaml| project are to:

- Integrate well with `Traits <https://github.com/enthought/traits>`_ and
  `Chaco <http://code.enthought.com/chaco/>`_ .
- Help **separate** the presentation and content (i.e., MVC)
- Allow a **single** script to work across *multiple* widget toolkits when
  using the default interfaces.
- Be **extensible** and allow adaptation and addition of the base widgets
  with little effort.

.. _dependencies:

Prerequisites
^^^^^^^^^^^^^

Enaml is developed using `Python <http://python.org/>`_ 2.7 and requires
recent (2012-current) versions of the following libraries:

*Required*:

- `Traits <https://github.com/enthought/traits>`_
- At least one backend toolkit:

  - `PySide <http://www.pyside.org/>`_
  - `PyQt4 <http://www.riverbankcomputing.co.uk/software/pyqt/intro>`_
  - `wxPython <http://www.wxpython.org/>`_ with a recent (> 0.9.1)
    `agw <http://xoomer.virgilio.it/infinity77/AGW_Docs/index.html>`_
    library
- `PLY <http://www.dabeaz.com/ply/>`_ (Python Lex-Yacc),
  for parsing *.enaml* files
- `casuarius <https://github.enthought.com/casuarius>`_ linear constraint
  solver.
- `distribute <http://pypi.python.org/pypi/distribute>`_ (package
  installation)

*Optional*:

- `Graphviz <http://www.graphviz.org/>`_ (used for documentation)


Installation
^^^^^^^^^^^^

To install the package please check out `the source from github
<https://github.com/enthought/enaml>`_

Then install with::

    python setup.py install

Alternatively you can work in developing mode::

    python setup.py develop

Next, take a look at the :ref:`tutorials.<tutorials-home>`
