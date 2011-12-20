.. _hello-world:

Hello World! tutorial
===============================================================================

This is a basic tutorial to explain the basic features of an |Enaml| user
interface. It uses sets up a minimal GUI to display a simple message.

Source
-------------------------------------------------------------------------------
Let's get started with a basic "hello world!" example:

An |Enaml| GUI comprises two components: the .enaml file (describing the view)
and the Python code to execute it. Our minimalist .enaml file describing a
message-displaying GUI is shown here (and can be downloaded :download:`here <../../../examples/hello_world/hello_world.enaml>`):

.. literalinclude:: ../../../examples/hello_world/hello_world.enaml
    :language: python

The Python code to use the GUI is shown here (and can be downloaded
:download:`here <../../../examples/hello_world/hello_world.py>`):

.. literalinclude:: ../../../examples/hello_world/hello_world.py
    :language: python

The resulting GUI looks like this (in Mac OS):

.. image:: images/hello_world.png

Walk-through
-------------------------------------------------------------------------------

Let's take a closer look at the files.

|Enaml| file
_______________________________________________________________________________

Comments
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

The file begins with some comment lines. As in Python code, ``#`` begins a
comment line and is ignored during lexing and parsing.

::

 #-----------------------------------------------------------------------------
 #  Copyright (c) 2011, Enthought, Inc.
 #  All rights reserved.
 #-----------------------------------------------------------------------------


``defn`` Block
-------------------------------------------------------------------------------

We use a ``defn`` block to construct a view that is available for external
Python functions to import.  The header line starts with the |Enaml| keyword
``defn`` and ends with a colon. With the header line, we specify any
*arguments* that will be passed in by the calling Python function.

::

 defn MyMessageToTheWorld(message):
     Window:
         Label:
             text = message

In this case, ``message`` is passed in as a parameter.  Next, we specify a
hierarchy tree of view components. As in Python, indentation is used to specify
code block structure.

Our view is made up of a ``Window`` (a :ref:`built-in component
<built-ins-ref>`) containing a ``Label``, whose ``text`` attribute we set
equal to ``message``, the parameter passed in by the calling function.

Python code
_______________________________________________________________________________

To use the view in Python code, first, we import |Enaml|:

::

 import enaml

Then we use ``enaml.imports()`` as a `context manager
<http://docs.python.org/release/2.5.2/ref/context-managers.html>`_ for importing
the |Enaml| view.
::

 with enaml.imports():
     from hello_world import MyMessageToTheWorld

Then, we instantiate the view:
::

 view = MyMessageToTheWorld("Hello, world!")

The ``show()`` method on ``view`` displays the window:
::

 view.show()
