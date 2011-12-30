Developer's corner
==================

This section describes a set of guidelines for the developers of the Enaml.

.. note:: The content of this section is currently under discussion and
   the guidelines are only suggestions.


GitHub Branches
---------------

The following table provides a summary of the main developing branches and
their purpose

================== ============================================
Label              Description
================== ============================================
``master``         main stable branch
``develop``        developing branch (unstable)
================== ============================================

Sphinx Source
-------------

For Sphinx source, please use 4 spaces for indention and a UTF-8 encoding.
The line length is preferred to be between 72-74 characters.

Due to the magic under the hood of the traits objects, automatically
extracting documentation from the source with the standard autodoc tools
is a little tricky. Enaml's Sphinx source should therefore use the following
conventions:

    - When documenting classes with Traits the sphinx directive
      ``.. autoattribute::`` does not work. To document single attributes
      use the (undocumented) ``.. autoattributeinstance::``  directive
      instead.
    - The ``..autoclass::`` directive works fine as long as specific
      members are not specified in the ``:members:`` context parameter.

Source Code
-----------

The coding style follows the `PEP 8 <http://www.python.org/dev/peps/pep-0008/>`_
guidelines and uses 4 spaces for indention. The maximum line length is 80
characters; however, the documentation is preferred to be between 72-74
characters.

Preamble
++++++++

The preamble of each file contains copyright notice. The following example
can be used as a template

.. include:: preamble.py
    :literal:

Docstrings
++++++++++

The current documentation uses the autodoc extension of the Sphinx
distribution. The autodoc parsing is also extended to convert heading-based
docstring descriptions to standard reStructedText role directives.

Traits classes
^^^^^^^^^^^^^^

In order to create autodoc-friendly docstrings for classes that inherit
from `traits.HasTraits`, please consider the following:

    - Avoid placing headings (except those that are described below) in
      the multi-line docstrings since they are not rendered properly by
      Sphinx.

    - Document the class attributes using one or multiple lines commented
      with ``#:`` before (i.e. above) the attribute definition. These will
      be picked up by the autodoc commands and used as the docstring for
      the following value::

        <other code>

        # this comment will not appear since it lacks the ':'
        #: The file name of the .qbc file to load
        filename = File

    - Alternative you can document the attributes at the main class using
      the Attribute heading. The current autodoc extension supports
      the following headings for classes:

      ========== ==========================================================
      Heading    Description
      ========== ==========================================================
      Methods    Class methods
      Attributes Set of attributes
      Notes      Useful notes (one paragraph)
      See Also   References
      ========== ==========================================================

For example, the Python code

.. include:: traits_class.py
    :literal:

leads to this Sphinx output (using ``..autoclass::``):

.. currentmodule:: traits_class

.. autoclass:: Myclass
    :members:

.. autoclass:: Otherclass
    :members:

Functions
^^^^^^^^^

In order to create autodoc-friendly docstrings for functions, please consider
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
    using the headings, the dosctring is also readable in interactive
    python sessions.


Example
~~~~~~~

::

        """Extract the fields from the docstring

        Parse the fields into tuples of name, type and description in a
        list of strings. The strings are also removed from the list.

        Arguments
        ---------
        indent : str, optional
            the indent argument is used to make sure that only the lines
            with the same indent are considered when checking for a
            field header line. The value is used to define the field
            checking function.

        field_check : function
            Optional function to use for checking if the next line is a
            field. The signature of the function is ``foo(line)`` and it
            should return ``True`` if the line contains a valid field
            The default function is checking for fields of the following
            formats::

                <name> : <type>

            or::

                <name> :

            Where the name has to be one word.

        Returns
        -------
        parameters : list of tuples
            list of parsed parameter tuples as returned from the
            :meth:`~BaseDocstring.parse_field` method.

        """

.. currentmodule:: refactor_doc

.. automethod:: FunctionDocstring.extract_fields
