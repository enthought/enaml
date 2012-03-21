#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import unittest

from enaml.validation import (
    NumberValidator, IntegralNumberValidator, RealNumberValidator,
    ComplexNumberValidator, IntValidator, LongValidator, FloatValidator,
    ComplexValidator, BinValidator, OctValidator, HexValidator,
    LongBinValidator, LongOctValidator, LongHexValidator,
)


@unittest.skip('Skipping Validation Tests')
class TestNumberValidators(unittest.TestCase):

    def test_number_validator(self):
        v = NumberValidator()
        self.assertEqual(v.validate(u'k'), v.INVALID)
        self.assertEqual(v.validate(u'12'), v.ACCEPTABLE)
        self.assertEqual(v.validate(u'-12'), v.ACCEPTABLE)
        self.assertEqual(v.validate(u'1e7'), v.ACCEPTABLE)

    def test_number_out_of_range(self):
        v = NumberValidator(low=10, high=89)
        self.assertEqual(v.validate(u'12'), v.ACCEPTABLE)
        self.assertEqual(v.validate(u'-12'), v.INVALID)
        self.assertEqual(v.validate(u'9'), v.INTERMEDIATE)
        self.assertEqual(v.validate(u'60k'), v.INVALID)
    
    def test_integral_number_validator(self):
        v = IntegralNumberValidator()

