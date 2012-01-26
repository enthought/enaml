.. _hello-world:

"Hello World" tutorial - Part II
===============================================================================

This is a basic tutorial to explain the basic features of an |Enaml| user
interface. It sets up a minimal GUI to display a simple message.

|Enaml| supports implementing a `model-view-controller architecture
<http://en.wikipedia.org/wiki/Model%E2%80%93view%E2%80%93controller>`_ . An
'.enaml' file describes the *view*, and the *model* is treated by Python code,
usually in the form of `Traits objects
<http://code.enthought.com/projects/traits/>`_ . The |Enaml| module handles
most/all of the *controller* aspects of the GUI.

Let's get started with a basic "hello world" example:

Here is our minimalist .enaml file describing a message-displaying GUI
(:download:`download here <../../../examples/hello_world/hello_world.enaml>`):

.. literalinclude:: ../../../examples/hello_world/hello_world.enaml
    :language: python

Here is the Python code to use the GUI (:download:`download here
<../../../examples/hello_world/hello_world.py>`):

.. literalinclude:: ../../../examples/hello_world/hello_world.py
    :language: python

The resulting GUI looks like this (in Mac OS):

.. image:: images/hello_world.png

Let's take a closer look at the |Enaml| file.

Comment Blocks
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

The .enaml file begins with some comment lines. As in Python code, ``#`` begins
a comment line and is ignored during lexing and parsing.

::

 #-----------------------------------------------------------------------------
 #  Copyright (c) 2011, Enthought, Inc.
 #  All rights reserved.
 #-----------------------------------------------------------------------------

.. _defn-block-tut:

``defn`` Blocks
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

Next, we use a ``defn`` block to construct a view that is available for
external Python functions to import. The syntax is similar to that of `Python
compound statements <http://docs.python.org/reference/compound_stmts.html>`_
. The header line starts with the |Enaml| keyword **defn** and ends with a
colon. With the header line, we specify any *arguments* that will be passed in
by the calling Python function. In this case, ``message`` is passed in as a
parameter.

::

 defn MyMessageToTheWorld(message):
     Window:
         Label:
             text = message

Next, we specify a hierarchy tree of view components. `As in Python
<http://docs.python.org/reference/lexical_analysis.html#indentation>`_ ,
indentation is used to specify code block structure. That is, statements
beginning at a certain indentation level refer to the header line at the next
lower indentation level.

Our view is made up of a ``Window`` containing a ``Label``, whose ``text``
attribute we set equal to ``message``, which is passed in by the calling
function.  (We'll discuss this in more detail in the :ref:`next tutorial
<john-doe>` .)

Using the |Enaml| view in Python
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

Now we'll take a look at how to use the view in Python code. First, we import
|Enaml|:

::

 import enaml

Then we use ``enaml.imports()`` as a `context manager
<http://docs.python.org/release/2.5.2/ref/context-managers.html>`_ for importing
the |Enaml| view.
::

 with enaml.imports():
     from hello_world import MyMessageToTheWorld

Then, we instantiate the view, passing the message to be displayed:
::

 view = MyMessageToTheWorld("Hello, world!")

The ``show()`` method on ``view`` displays the window:
::

 view.show()


.. image:: images/hello_world.png
