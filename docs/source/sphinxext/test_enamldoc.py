import unittest
from enamldoc import FunctionDocstring, ClassDocstring

class TestBaseDocString(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_refactor(self):
        self.fail()

    def testparse(self):
        self.fail()

    def testis_field(self):
        self.fail()

    def testis_method(self):
        self.fail()

    def test_extract_parameters(self):
        self.fail()

    def test_parse_parameter(self):
        self.fail()

    def test_indent(self):
        self.fail()

    def test_is_section(self):
        self.fail()

    def testinsert_lines(self):
        self.fail()

    def testget_indent(self):
        self.fail()

    def testmove_forward(self):
        self.fail()

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
        pass

    def tearDown(self):
        pass

    def test_refactor_attributes(self):
        self.fail()

    def test_refactor_methods(self):
        self.fail()

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

    I have no clue why am I doing this.
    """

        rst = \
    """ This is a sample class docstring

    .. note::
        This is the test.
        Wait we have not finished.

    I have no clue why am I doing this.
    """

        docstring_lines = docstring.splitlines()
        ClassDocstring(docstring_lines, verbose=True)
        output = '\n'.join(docstring_lines)
        self.assertMultiLineEqual(rst, output)

if __name__ == '__main__':
    unittest.main()
