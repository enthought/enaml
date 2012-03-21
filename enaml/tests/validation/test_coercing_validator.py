#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import unittest

from enaml.validation import CoercingValidator


@unittest.skip('Skipping Validation Tests')
class TestCoercingValidator(unittest.TestCase):

    def test_all_valid(self):
        v = CoercingValidator()
        for item in (u'foo', u'12', u'foo12', u'#$@$@#$%!@#'):
            self.assertEqual(v.validate(item), v.ACCEPTABLE)
    
    def test_thru_convert(self):
        v = CoercingValidator()
        for item in (u'foo', u'12', u'foo12', u'#$@$@#$%!@#'):
            self.assertEqual(v.convert(item), item)
    
    def test_thru_format(self):
        v = CoercingValidator()
        for item in (u'foo', u'12', u'foo12', u'#$@$@#$%!@#'):
            self.assertEqual(v.format(item), item)
    
    def test_default_format(self):
        v = CoercingValidator()
        for item in (42, 42.0, object, object()):
            self.assertEqual(v.format(item), unicode(item))
    
    def test_convert_func(self):
        v = CoercingValidator(converter=int)
        for item in (u'42', u'456', u'789'):
            self.assertEqual(v.convert(item), int(item))

    def test_coerce_func(self):
        v = CoercingValidator(coercer=int)
        for item in (u'42', u'456', u'789'):
            self.assertEqual(v.convert(item), int(item))
        
    def test_format_func(self):
        fmt = lambda val: unicode(val) + u'foo'
        v = CoercingValidator(formatter=fmt)
        for item in (u'42', u'45.6', u'78.9'):
            self.assertEqual(v.format(item), item + u'foo')

    def test_normalize(self):
        v = CoercingValidator(converter=float, coercer=int)
        self.assertEqual(v.normalize(u'12.3'), u'12')

    def test_convert_coerce_func(self):
        v = CoercingValidator(converter=float, coercer=int)
        for item, res in ((u'42', 42), (u'67.98', 67)):
            self.assertEqual(v.convert(item), res)

    def test_has_locale(self):
        v = CoercingValidator()
        self.assertTrue(v.locale is not None)

    def test_locale_raises(self):
        v = CoercingValidator()
        with self.assertRaises(TypeError):
            v.locale = 12

    def test_locale_allow_none(self):
        v = CoercingValidator()
        v.locale = None

