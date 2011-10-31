#------------------------------------------------------------------------------
#  file: test_refactor_doc.py
#  License: LICENSE.TXT
#
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import unittest
from refactor_doc import FunctionDocstring, ClassDocstring

class TestFunctionDocstring(unittest.TestCase):

    def setUp(self):
        self.maxDiff = None

    def tearDown(self):
        pass

    def test_refactor_returns(self):
        docstring =\
    """ This is a sample function docstring.

    Returns
    -------
    myvalue : list
        A list of important values.
        But we need to say more things about it.

    """

        rst = \
    """ This is a sample function docstring.

    :returns:
        **myvalue** (list) - A list of important values. But we need to say more things about it.

    """

        docstring_lines = docstring.splitlines()
        FunctionDocstring(docstring_lines)
        output = '\n'.join(docstring_lines)
        self.assertMultiLineEqual(rst, output)

    def test_refactor_raises(self):
        docstring =\
    """ This is a sample function docstring.

    Raises
    ------
    TypeError :
        This is the first paragraph of the description.
        More description.

    ValueError :
        Description of another case where errors are raised.

    """

        rst = \
    """ This is a sample function docstring.

    :raises:
        - **TypeError** - This is the first paragraph of the description. More description.
        - **ValueError** - Description of another case where errors are raised.

    """

        docstring_lines = docstring.splitlines()
        FunctionDocstring(docstring_lines)
        output = '\n'.join(docstring_lines)
        self.assertMultiLineEqual(rst, output)

    def test_refactor_arguments(self):
        docstring =\
    """ This is a sample function docstring

    Arguments
    ---------
    inputa : str
        The first argument holds the first input!.

        This is the second paragraph.

    inputb : float
        The second argument is a float.
        the default value is 0.

        .. note:: this is an optional value.

    """

        rst = \
    """ This is a sample function docstring

    :param inputa: The first argument holds the first input!.

            This is the second paragraph.
    :type inputa: str
    :param inputb: The second argument is a float.
            the default value is 0.

            .. note:: this is an optional value.
    :type inputb: float

    """

        docstring_lines = docstring.splitlines()
        FunctionDocstring(docstring_lines)
        output = '\n'.join(docstring_lines)
        self.assertMultiLineEqual(rst, output)

    def test_refactor_notes(self):
        docstring =\
    """ This is a sample function docstring.

    Notes
    -----
    This is the test.
    Wait we have not finished.

    This should not be included.
    """

        rst = \
    """ This is a sample function docstring.

    .. note::
        This is the test.
        Wait we have not finished.

    This should not be included.
    """

        docstring_lines = docstring.splitlines()
        FunctionDocstring(docstring_lines)
        output = '\n'.join(docstring_lines)
        self.assertMultiLineEqual(rst, output)

    def test_docstring_cases_1(self):
        docstring =""" Sets the selection to the bounds of start and end.

        If the indices are invalid, no selection will be made,
        and any current selection will be cleared.

        Arguments
        ---------
        start : Int
            The start selection index, zero based.

        end : Int
            The end selection index, zero based.

        Returns
        -------
        result : None

        """

        rst =""" Sets the selection to the bounds of start and end.

        If the indices are invalid, no selection will be made,
        and any current selection will be cleared.

        :param start: The start selection index, zero based.
        :type start: Int
        :param end: The end selection index, zero based.
        :type end: Int

        :returns:
            **result** (None)

        """

        docstring_lines = docstring.splitlines()
        FunctionDocstring(docstring_lines)
        output = '\n'.join(docstring_lines)
        self.assertMultiLineEqual(rst, output)


class TestClassDocstring(unittest.TestCase):

    def setUp(self):
        self.maxDiff = None

    def tearDown(self):
        pass

    def test_refactor_attributes(self):
        docstring =\
    """Base abstract docstring refactoring class.

    The class' main purpose is to parse the dosctring and find the
    sections that need to be refactored. It also provides a number of
    methods to help with the refactoring. Subclasses should provide
    the methods responsible for refactoring the sections.

    Attributes
    ----------
    docstring : list
        A list of strings (lines) that holds docstrings

    index : int
        The current zero-based line number of the docstring that is
        proccessed.
    """

        rst = \
    """Base abstract docstring refactoring class.

    The class' main purpose is to parse the dosctring and find the
    sections that need to be refactored. It also provides a number of
    methods to help with the refactoring. Subclasses should provide
    the methods responsible for refactoring the sections.

    .. attribute:: docstring
        *(list)*
        A list of strings (lines) that holds docstrings

    .. attribute:: index
        *(int)*
        The current zero-based line number of the docstring that is
        proccessed.
    """

        docstring_lines = docstring.splitlines()
        ClassDocstring(docstring_lines, verbose=True)
        output = '\n'.join(docstring_lines)
        self.assertMultiLineEqual(rst, output)

    def test_refactor_methods(self):
        docstring =\
    """ This is a sample class docstring

    Methods
    -------
    extract_fields(indent='', field_check=None)
        Extract the fields from the docstring

    get_field()
        Get the field description.

    get_next_paragraph()
        Get the next paragraph designated by an empty line.
    """

        rst = \
    """ This is a sample class docstring

    ========================== ===================================================
    Methods                    Descriptions
    ========================== ===================================================
    :meth:`extract_fields`     Extract the fields from the docstring
    :meth:`get_field`          Get the field description.
    :meth:`get_next_paragraph` Get the next paragraph designated by an empty line.
    ========================== ===================================================
    """

        docstring_lines = docstring.splitlines()
        ClassDocstring(docstring_lines)
        output = '\n'.join(docstring_lines)
        self.assertMultiLineEqual(rst, output)


    def testmax_lengths(self):
        self.fail()

    def testreplace_at(self):
        self.fail()

    def test_refactor_see_also(self):
        self.fail()

    def test_refactor_notes(self):
        docstring =\
    """ This is a sample class docstring

    Notes
    -----
    This is the test.
    Wait we have not finished.

    This is not a note.
    """

        rst = \
    """ This is a sample class docstring

    .. note::
        This is the test.
        Wait we have not finished.

    This is not a note.
    """

        docstring_lines = docstring.splitlines()
        ClassDocstring(docstring_lines)
        output = '\n'.join(docstring_lines)
        self.assertMultiLineEqual(rst, output)

if __name__ == '__main__':
    unittest.main()
