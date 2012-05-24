.. _hello-world:

"Hello World" tutorial
===============================================================================

Our goal in this tutorial is to show a minimal example of an |Enaml| user
interface and introduce a few basic concepts. It sets up a minimal GUI to
display a simple message.

Let's get started with a minimalist "hello world" example. |Enaml| interfaces
are described in a file with the ".enaml" extension. While the code has some
similarities to Python, |Enaml| is a separate language.

Here is our minimalist .enaml file describing a message-displaying GUI
(:download:`download here <../../../examples/hello_world/hello_world_view.enaml>`):

.. literalinclude:: ../../../examples/hello_world/hello_world_view.enaml
    :language: python

Use the special helper function ``enaml-run`` to run it from the command line
with ::

    $ enaml-run hello_world_view.enaml

The resulting GUI looks like this (in Mac OS):

.. image:: images/hello_world.png

Let's take a closer look at the |Enaml| file.

Enaml Definitions
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

An |Enaml| view is made up of a series of component *definitions* that look a
lot like Python classes. In the first line of code, we are defining a new
component, ``Main``, which derives from ``MainWindow``, a component in the
|Enaml| standard library.

::

    enamldef Main(MainWindow):

With the this line of code, we have defined the start of a *definition
block*.

In general, we could call this almost anything we want, as long as it is a
Python-valid name. In this case, however, by giving it the special name "Main"
we get to run it from the command line with the special ``enaml-run``
tool. ``enaml-run`` looks for a component named "Main" or a function named
"main" and runs it as a standalone application.


Definition Structure
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

Inside a definition block, the view is defined in a hierarchical tree of view
components. `As in Python
<http://docs.python.org/reference/lexical_analysis.html#indentation>`_ ,
indentation is used to specify code block structure. That is, statements
beginning at a certain indentation level refer to the header line at the next
lower indentation level. So in our simple example, the ``Container:`` belongs to
``Main`` and the ``Label:`` belongs to ``Container``::

    enamldef Main(MainWindow):
        attr message = "Hello, world!"
        Container:
            Label:
                text = message


Our view is made up of a ``MainWindow`` containing a ``Container`` which in
turn contains a ``Label``, whose ``text`` attribute we set equal to ``message``
attribute of ``Main``, which can be passed in by the
calling function, but which has a default of ``Hello, world!``.  (We'll discuss
this in more detail in the :ref:`next tutorial <john-doe>` .)

Using the |Enaml| view in Python
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

Now we'll take a look at how to use the view in Python code. First, we import
|Enaml|::

 import enaml

Then we use ``enaml.imports()`` as a `context manager
<http://docs.python.org/release/2.5.2/ref/context-managers.html>`_ for importing
the |Enaml| view.
::

 with enaml.imports():
     from hello_world_view import Main

Then, we instantiate the view, passing the message to be displayed::

 view = Main("Hello, world, from Python!")

The ``show()`` method on ``view`` displays the window and starts the application
mainloop::

 view.show()


.. image:: images/hello_world_python.png
