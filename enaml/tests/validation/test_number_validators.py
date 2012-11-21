#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import unittest

from enaml.validation.api import (
    IntValidator, FloatValidator, RegexValidator
)


class ValidatorTestCase(unittest.TestCase):
    """ Simple class exposing assertValid and asertInvalid methods to test
    validators. """

    def assertValid(self, validator, value):
        self.assertTrue(validator.validate(value, None)[1])

    def assertInvalid(self, validator, value):
        self.assertFalse(validator.validate(value, None)[1])


class TestIntValidator(ValidatorTestCase):

    def test_int_validator(self):
        v = IntValidator()
        self.assertInvalid(v, u'k')
        self.assertValid(v, u'12')
        self.assertValid(v, u'-12')
        self.assertInvalid(v, u'1e7')

    def test_number_out_of_range(self):
        v = IntValidator(minimum=10, maximum=89)
        self.assertValid(v, u'12')
        self.assertInvalid(v, u'-12')
        self.assertInvalid(v, u'9')
        self.assertInvalid(v, u'60k')


class TestFloatValidator(ValidatorTestCase):

    def test_int_validator(self):
        v = FloatValidator()
        self.assertInvalid(v, u'k')
        self.assertValid(v, u'12')
        self.assertValid(v, u'-12')
        self.assertValid(v, u'1e7')

    def test_number_out_of_range(self):
        v = FloatValidator(minimum=10, maximum=89)
        self.assertValid(v, u'12')
        self.assertInvalid(v, u'-12')
        self.assertInvalid(v, u'9')
        self.assertInvalid(v, u'60k')

    def test_validator_no_exponent(self):
        v = FloatValidator(allow_exponent=False, minimum=10)
        self.assertValid(v, u'12')
        self.assertInvalid(v, u'9')
        self.assertInvalid(v, u'60k')
