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
        pass

    def tearDown(self):
        pass

    def test_refactor_returns(self):
        self.fail()

    def test_refactor_raises(self):
        self.fail()

    def test_refactor_arguments(self):
        self.fail()

    def test_refactor_notes(self):
        docstring =\
    """ This is a sample function docstring

    Notes
    -----
    This is the test.
    Wait we have not finished.

    I have no clue why am I doing this.
    """

        rst = \
    """ This is a sample function docstring

    .. note::
        This is the test.
        Wait we have not finished.

    I have no clue why am I doing this.
    """

        docstring_lines = docstring.splitlines()
        FunctionDocstring(docstring_lines, verbose=True)
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
