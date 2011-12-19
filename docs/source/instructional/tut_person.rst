.. _hello-john-doe

Hello John Doe tutorial
===============================================================================

This is a basic tutorial to explain the basic features of an |Enaml| user
interface. It uses sets up a GUI with the name and age of a person.

Source
-------------------------------------------------------------------------------

:download:`.enaml file <../../../examples/person/person_view.enaml>`

:download:`Python file <../../../examples/person/person.py>`

Let's get started with a basic hello-world type example. We will create a GUI
to view or change the information about a person.

An |Enaml| GUI comprises two components: the .enaml file (describing the view)
and the Python code to execute it. The .enaml file describing a person for our
example is shown here (and can be downloaded from the link above):

.. literalinclude:: ../../../examples/person/person_view.enaml
    :language: python

The Python code to use the GUI is shown here (and can be downloaded from the
other link above):

.. literalinclude:: ../../../examples/person/person_view.enaml
    :language: python

The resulting GUI looks like this (in Mac OS):

.. image:: images/john_doe.png

Walk-through
-------------------------------------------------------------------------------

Let's take a closer look at the files.

The file begins with some comment lines. As in Python code, `#` begins a
comment line and is ignored during lexing and parsing.

::

 #-----------------------------------------------------------------------------
 #  Copyright (c) 2011, Enthought, Inc.
 #  All rights reserved.
 #-----------------------------------------------------------------------------

Imports also work as they do in Python. In this case, we are importing the
integer field widget :py:class:`IntField`.

::

 from enaml.stdlib.fields import IntField


