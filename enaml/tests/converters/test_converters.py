#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import datetime

from enaml import converters

from .converter_test_case import ConverterTestCase


class TestBaseConverter(ConverterTestCase):
    """ Test the base Converter class.

    """
    def test_abstract(self):
        """ Make sure that this class cannot be instantiated.

        """
        self.assertRaises(TypeError, converters.Converter)


class TestCustomConverter(ConverterTestCase):
    """ Check that the abstract methods on Converter must be implemented.

    """
    def test_converter_without_from_component(self):
        """ The abstract method 'from_component' must be implemented.

        """
        class NoFromComponent(converters.Converter):

            def to_component(self, value):
                return value

        with self.assertRaises(TypeError):
            NoFromComponent()

    def test_converter_without_to_component(self):
        """ The abstract method 'to_component' must be implemented.

        """
        class NoToComponent(converters.Converter):

            def from_component(self, value):
                return value

        with self.assertRaises(TypeError):
            NoToComponent()

    def test_custom_converter(self):
        """ Instantiate a proper custom Converter.

        """
        class CustomConverter(converters.Converter):

            def from_component(self, value):
                return value

            def to_component(self, value):
                return value

        # This instantiation will succeed.
        CustomConverter()


class TestNullConverter(ConverterTestCase):
    """ Test the null converter.

    """
    def setUp(self):
        """ Create a NullConverter

        """
        self.converter = converters.NullConverter()

    def test_symmetry(self):
        """ Test that the 'to_component' and 'from_component' methods 
        are symmetric.

        """
        self.assertConverterSymmetric(self.converter, [1, '2'], [1, '2'])


class TestStringConverter(ConverterTestCase):
    """ Test the string converter, which converts inputs and outputs to
    strings.

    """
    def setUp(self):
        """ Create a StringConverter.

        """
        self.converter = converters.StringConverter()

    def test_symmetry(self):
        """ Test that the 'to_component' and 'from_component' methods are
        symmetric.

        """
        self.assertConverterSymmetric(self.converter, 'Hello', 'Hello')


class TestIntConverter(ConverterTestCase):
    """ Test the integer converter.

    """
    def setUp(self):
        """ Create an IntConverter.

        """
        self.converter = converters.IntConverter()

    def test_symmetry(self):
        """ Test that the 'to_component' and 'from_component' methods are
        symmetric.

        """
        self.assertConverterSymmetric(self.converter, '42', 42)

    def test_empty_string_conversion_failure(self):
        """ Test that the empty string cannot be converted.

        """
        self.assertRaises(ValueError, self.converter.from_component, '')


class TestHexConverter(ConverterTestCase):
    """ Test the hexadecimal converter.

    """
    def setUp(self):
        """ Create a HexConverter.

        """
        self.converter = converters.HexConverter()

    def test_symmetry(self):
        """ Test that the 'to_component' and 'from_component' methods are
        symmetric.

        """
        self.assertConverterSymmetric(self.converter, '0xabc', 2748)

    def test_empty_string_conversion_failure(self):
        """ Test that the empty string cannot be converted.

        """
        self.assertRaises(ValueError, self.converter.from_component, '')


class TestOctalConverter(ConverterTestCase):
    """ Test the octal converter.

    """
    def setUp(self):
        """ Create an OctalConverter.

        """
        self.converter = converters.OctalConverter()

    def test_symmetry(self):
        """ Test that the 'to_component' and 'from_component' methods are
        symmetric.

        """
        self.assertConverterSymmetric(self.converter, '0555', 365)

    def test_empty_string_conversion_failure(self):
        """ Test that the empty string cannot be converted.

        """
        self.assertRaises(ValueError, self.converter.from_component, '')


class TestFloatConverter(ConverterTestCase):
    """ Test the float converter.

    """
    def setUp(self):
        """ Create an instance of FloatConverter.

        """
        self.converter = converters.FloatConverter()

    def test_symmetry(self):
        """ Test that the 'to_component' and 'from_component' methods are
        symmetric.

        """
        self.assertConverterSymmetric(self.converter, '867.5309', 867.5309)

    def test_int_symmetry(self):
        """ Test this converter's symmetry on an integer value.

        """
        self.assertConverterSymmetric(self.converter, '42', 42)

    def test_empty_string_conversion_failure(self):
        """ Test that the empty string cannot be converted.

        """
        self.assertRaises(ValueError, self.converter.from_component, '')


class TestDateConverter(ConverterTestCase):
    """ Test the date converter.

    """
    def test_default_format(self):
        """ Test a default instance of DateConverter.

        """
        converter = converters.DateConverter()
        date = datetime.date(2002, 2, 22)
        self.assertConverterSymmetric(converter, '2002-02-22', date)

    def test_custom_format(self):
        """ Test DateConverter with a custom format string.

        """
        converter = converters.DateConverter('%B %d, %Y')
        test_date = datetime.date(1996, 2, 29)
        test_text = test_date.strftime('%B %d, %Y')
        self.assertConverterSymmetric(converter, test_text, test_date)


class TestDateTimeConverter(ConverterTestCase):
    """ Test the datetime converter.

    """
    def test_default_format(self):
        """ Test the a default instance of DateTimeConverter

        """
        converter = converters.DateTimeConverter()
        dt =  datetime.datetime(1991, 8, 19, 20, 2)
        self.assertConverterSymmetric(converter, '1991-08-19T20:02:00', dt)

    def test_custom_format(self):
        """ Test DateTimeConverter with a custom format string.

        """
        converter = converters.DateTimeConverter('%I:%M on %m/%d/%Y')
        dt = datetime.datetime(1979, 4, 20, 0, 1)
        self.assertConverterSymmetric(converter, '12:01 on 04/20/1979', dt)

