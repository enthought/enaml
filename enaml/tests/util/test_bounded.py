#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import unittest
from datetime import date

from traits.api import (HasStrictTraits, TraitError, Float, Instance, Date)

from enaml.core.trait_types import Bounded

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

class Test_Bounded_Special(unittest.TestCase):
    """ Test special use cases for the Bounded trait.

    """
    def test_inner_bound_class(self):
        """ Test dynamic initialization with inner class.

        """
        class small_class(HasStrictTraits):
            low = Float(0)
            high = Float(2)

        class main_class(HasStrictTraits):
            bounds = Instance(small_class, ())
            value = Bounded(0.2, 'bounds.low', 'bounds.high')

        instance = main_class()
        instance.value = 0.2
        self.assertAlmostEqual(instance.value, 0.2)

        with self.assertRaises(TraitError):
            instance.value = -1

    def test_bounded_traits(self):
        """ Test initialization with Trait Class

        """
        class main_class(HasStrictTraits):
            value = Bounded(Date(date(2007,12, 18)),
                            date(2003,12, 18),
                            date(2010,12, 18))

        instance = main_class()
        self.assertEqual(instance.value, date(2007,12, 18))

        with self.assertRaises(TraitError):
            instance.value = 0.2

        instance.value = date(2008,12, 18)
        self.assertEqual(instance.value, date(2008,12, 18))

    def test_bounded_python(self):
        """ Test initialization wiht complex python object.

        """
        class main_class(HasStrictTraits):
            value = Bounded(date(2007,12, 18),
                            date(2003,12, 18),
                            date(2010,12, 18))

        instance = main_class()
        self.assertEqual(instance.value, date(2007,12, 18))
        with self.assertRaises(TraitError):
            instance.value = 0.2

        instance.value = date(2008,12, 18)
        self.assertEqual(instance.value, date(2008,12, 18))