#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import unittest

from traits.api import (HasStrictTraits, TraitError, Float,
                        Callable, Instance)

from enaml.util.trait_types import Bounded
from enaml.converters import (Converter, PassThroughConverter,
                              SliderLogConverter)

class Test_Bounded_Static(unittest.TestCase):
    """ Test the use of the Bounded trait with static bounds.

    """
    @classmethod
    def setUpClass(self):

        class my_class(HasStrictTraits):

            value = Bounded(0.2, 0, 4)

        self.traits_class = my_class

    def setUp(self):
        self.traits_instance = self.traits_class()

    def test_init(self):
        """ Test basic static initialization """
        value = self.traits_instance.value
        self.assertAlmostEqual(value, 0.2)

    def test_assigment(self):
        """ Test static assigment """
        instance = self.traits_instance
        instance.value = 0.7
        self.assertAlmostEqual(instance.value, 0.7)

    def test_invalid(self):
        """ Test static assigment """
        instance = self.traits_instance
        with self.assertRaises(TraitError):
            instance.value = -2

class Test_Bounded_Dynamic(unittest.TestCase):
    """ Test the use of the Bounded trait with dynamic bounds.

    """
    @classmethod
    def setUpClass(self):

        class my_class(HasStrictTraits):

            low = Float(0)
            high = Float(4)
            value = Bounded(0.2, low='low', high='high')

        self.traits_class = my_class

    def setUp(self):
        self.traits_instance = self.traits_class()

    def test_init(self):
        """ Test dynamic initialization. """
        value = self.traits_instance.value
        self.assertAlmostEqual(value, 0.2)

    def test_assigment(self):
        """ Test assigment. """
        instance = self.traits_instance
        instance.value = 0.7
        self.assertAlmostEqual(instance.value, 0.7)

    def test_invalid(self):
        """ Test invalid assigment. """
        instance = self.traits_instance
        with self.assertRaises(TraitError):
            instance.value = -2

    def test_change_lower(self):
        """ Test changing the lower bound. """
        instance = self.traits_instance
        instance.low = -4.0
        instance.value = -2
        self.assertAlmostEqual(instance.value, -2)

    def test_change_upper(self):
        """ Test changing the upper bound. """
        instance = self.traits_instance
        instance.high =  6.0
        instance.value =  5.7
        self.assertAlmostEqual(instance.value, 5.7)

class Test_Bounded_Dynamic_Function(unittest.TestCase):
    """ Test the use of the Bounded trait with dynamic converter function.

    """
    @classmethod
    def setUpClass(self):

        class my_class(HasStrictTraits):

            converter = Callable(lambda val: val/2.0)
            value = Bounded(0.2, 0, 2, converter='converter')

        self.traits_class = my_class

    def setUp(self):
        self.traits_instance = self.traits_class()

    def test_init(self):
        """ Test dynamic initialization. """
        value = self.traits_instance.value
        self.assertAlmostEqual(value, 0.2)

    def test_assigment(self):
        """ Test assigment. """
        instance = self.traits_instance
        instance.value = 4
        self.assertAlmostEqual(instance.value, 4)

    def test_invalid(self):
        """ Test invalid assigment. """
        instance = self.traits_instance
        with self.assertRaises(TraitError):
            instance.value = -2

    def test_set_converter_function(self):
        """ Test changing the converter function. """
        instance = self.traits_instance
        instance.converter = lambda val: val
        with self.assertRaises(TraitError):
            instance.value = 4

class Test_Bounded_Dynamic_Converter(unittest.TestCase):
    """ Test the use of the Bounded trait with dynamic Converter class.

    """
    @classmethod
    def setUpClass(self):

        class my_class(HasStrictTraits):

            converter = Instance(Converter, SliderLogConverter())
            value = Bounded(0.2, 0, 2, converter='converter')

        self.traits_class = my_class

    def setUp(self):
        self.traits_instance = self.traits_class()

    def test_init(self):
        """ Test dynamic initialization. """
        value = self.traits_instance.value
        self.assertAlmostEqual(value, 0.2)

    def test_assigment(self):
        """ Test assigment. """
        instance = self.traits_instance
        instance.value = 4
        self.assertAlmostEqual(instance.value, 4)

    def test_invalid(self):
        """ Test invalid assigment. """
        instance = self.traits_instance
        with self.assertRaises(TraitError):
            instance.value = -2

    def test_set_converter_class(self):
        """ Test changing the converter function. """
        instance = self.traits_instance
        instance.converter = PassThroughConverter()
        instance.value = 0.1
        self.assertAlmostEqual(instance.value, 0.1)


class Test_Bounded_Special(unittest.TestCase):
    """ Test special use cases for the Bounded trait.

    """
    def test_inner_bound_class(self):
        class small_class(HasStrictTraits):
            low = Float(0)
            high = Float(2)

        class main_class(HasStrictTraits):
            bounds = Instance(small_class, ())
            value = Bounded(0.2, 'bounds.low', 'bounds.high')

        instance = main_class()
        """ Test dynamic initialization. """
        instance.value = 0.2
        self.assertAlmostEqual(instance.value, 0.2)

        with self.assertRaises(TraitError):
            instance.value = -1
