Developer's corner
==================

This section describes a set of guidelines for the developers of the TraitsML.

.. note:: The content of this section is currently under discussion and the
    guidelines are only suggestions.


Github branches
---------------

The following table provides a summary of the main developing branches and
their purpose

==================  ============================================
label               description
==================  ============================================
``master``          main stable branch
``documentation``   temporary branch for the documentation tools
``wx``              wxWidget backend development
``pyside``          PySide backend development
``parsing``         Future work for replacing the ply parser
==================  ============================================


Docstrings
----------

To document the source code the current documentation is utilising the
autodoc extension of the sphinx distribution. The autodoc parsing is also
extended to provide a simple function/method docsting description.

Traits classes
^^^^^^^^^^^^^^

In order to create autodoc friendly docstrings for classes that have
please consider the following:

    - Avoid placing headings in the multiline docstrings since they are not
      parsed by autodoc.

    - Document the class attributes using one or multiple lines commented with
      ``#:`` before (i.e. above) the attribute definition. These will be picked
      up by the autodoc commands and used as the docstring for the current::

        <other code>

        # this comment will not appear since it lacks the ':'
        #: The file name of the qbc file to load
        filename = File

    - When documenting classes with Traits the directive ``.. autoattribute::``
      does not work. To document single attributes use the (undocumented)
      ``.. autoattribureinstance::``  directive instead.
    - The ``..autoclass::`` directive works fine as long as specific members
      are not specified in the ``:members:`` context parameter.


example:

The python code is:

.. include:: traits_sample.py
    :literal:

And the sphinx output using ``..autoclass::`` is:

.. currentmodule:: traits_sample

.. autoclass:: Myclass
    :members:

Functions
^^^^^^^^^

.. todo:: Create a better parser for the function documentation based on the
    numpydoc code




