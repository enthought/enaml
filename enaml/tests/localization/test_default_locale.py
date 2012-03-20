#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import locale
import unittest

from enaml.localization import (
    SystemLocale, get_default_locale, set_default_locale,
)


class TestDefaultLocale(unittest.TestCase):

    def setUp(self):
        self.old = get_default_locale()
        set_default_locale(None)
    
    def tearDown(self):
        set_default_locale(self.old)

    def test_system_default_locale(self):
        l = get_default_locale()
        self.assertIsInstance(l, SystemLocale)

    def test_system_locale_types(self):
        l = get_default_locale()
        name, enc = locale.getlocale()
        self.assertEqual(l.name, name)
        self.assertEqual(l.encoding, enc)

