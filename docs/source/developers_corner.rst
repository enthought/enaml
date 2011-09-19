Developer's corner
==================

This section describes a set of guidelines for the developers of the enaml.

.. note:: The content of this section is currently under discussion and
   the guidelines are only suggestions.


Github branches
---------------

The following table provides a summary of the main developing branches and
their purpose

================== ============================================
label              description
================== ============================================
``master``         main stable branch
``documentation``  temporary branch for the documentation tools
``wx``             wxWidget backend development
``pyside``         PySide backend development
``parsing``        Future work for replacing the ply parser
================== ============================================

Sphinx source
-------------

For sphinx source please use 4 spaces for indention and a utf-8 encoding.
The line length is preferred to be between 72-74 characters.

Due to the magic under the hood of the trait objects, automatically
extracting documentation from the source with the standard autodoc tools
is a little tricky. To this extent the sphinx source should take notice on
the following:

    - When documenting classes with Traits the sphinx directive
      ``.. autoattribute::`` does not work. To document single attributes
      use the (undocumented) ``.. autoattribureinstance::``  directive
      instead.
    - The ``..autoclass::`` directive works fine as long as specific
      members are not specified in the ``:members:`` context parameter.

Source Code
-----------

The coding style follow the pep8 guidelines using 4 spaces for indention.
The line length is 80 characters. However the documentation is preferred to
be between 72-74 characters.

Preamble
++++++++

The preamble of each file contains a small summary, the name of the author
and the date of the last revision. The following example can be used as a
template

.. include:: preamble.py
    :literal:

Docstrings
++++++++++

To document the source code the current documentation is utilising the
autodoc extension of the sphinx distribution. The autodoc parsing is also
extended to convert heading based docstring description to standard rst
based role directives.

Traits classes
^^^^^^^^^^^^^^

In order to create autodoc friendly docstrings for classes that have
please consider the following:

    - Avoid placing headings (except those that are described below) in
      the multi-line docstrings since they are not rendered properly by
      sphinx.

    - Document the class attributes using one or multiple lines commented
      with ``#:`` before (i.e. above) the attribute definition. These will
      be picked up by the autodoc commands and used as the docstring for
      the current::

        <other code>

        # this comment will not appear since it lacks the ':'
        #: The file name of the qbc file to load
        filename = File

    - Alternative you can document the attributes at the main class using
      the Attribute heading. However, in this case the description and
      usage of the attribute is way from the actual definition. The
      current autodoc extension supports the following headings for
      classes

      ========== =========================================
      Heading    Description
      ========== =========================================
      Attributes Set of class attributes and their usage
      ========== =========================================

In the following example the python code is:

.. include:: traits_class.py
    :literal:

And the sphinx output using ``..autoclass::`` is:

.. currentmodule:: traits_class

.. autoclass:: Myclass
    :members:


.. autoclass:: Otherclass
    :members:

Functions
^^^^^^^^^

In order to create autodoc friendly docstrings for functions please consider
the following:

    - The current parser extension supports the following headings for
      functions:

      ========= ==========================================================
      Heading   Description
      ========= ==========================================================
      Arguments Set of function arguments and their usage
      Returns   Return values of the function
      Raises    Errors and the cases in which they are raised
      Yields    Successive results of the generator
      ========= ==========================================================

    - Each section/heading can accept items with one of the following
      structures (spaces around ``:`` are important)::

        <heading>
        ---------
        <name> : <type>
            <description>

        <name> : <type>
            <description>

        <name> :
            <description>

        <heading>
        ---------
            <description>

      The last form is useful when a paragraph is more appropriate than a
      an item list.

    - Empty headings are removed and do not appear in the sphinx
      documentation

.. note:: The use of the headings is optional. The developer can use
    directly the rst role directives to format the docstrings. However,
    using the headings allows the dosctring to be readable in interactive
    python sessions.


example:

.. currentmodule:: enamldoc

.. automethod:: FunctionDocstring._extract_parameters









