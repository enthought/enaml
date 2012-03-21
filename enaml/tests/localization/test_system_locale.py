#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import datetime
import locale
import sys
import unittest

from enaml.localization import SystemLocale


@unittest.skip('Skipping locale tests')
class TestSystemLocale(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        if sys.platform == 'win32':
            locale.setlocale(locale.LC_ALL, 'usa')
        else:
            locale.setlocale(locale.LC_ALL, ('en_US', 'UTF-8'))
    
    @classmethod
    def tearDownClass(cls):
        locale.setlocale(locale.LC_ALL, 'C')

    def setUp(self):
        self.locale = SystemLocale.default()

    def tearDown(self):
        del self.locale
    
    def test_name(self):
        self.assertEqual(self.locale.name, u'en_US')
    
    def test_encoding(self):
        self.assertEqual(self.locale.encoding, u'UTF-8')
    
    def test_am_string(self):
        self.assertEqual(self.locale.am_string, u'AM')
    
    def test_pm_string(self):
        self.assertEqual(self.locale.pm_string, u'PM')
    
    def test_decimal_point(self):
        self.assertEqual(self.locale.decimal_point, u'.')
    
    def test_monetary_decimal_point(self):
        self.assertEqual(self.locale.monetary_decimal_point, u'.')
    
    def test_exponential(self):
        self.assertEqual(self.locale.exponential, u'e')
    
    def test_thousands_separator(self):
        self.assertEqual(self.locale.thousands_separator, u',')
    
    def test_monetary_thousands_separator(self):
        self.assertEqual(self.locale.monetary_thousands_separator, u',')
    
    def test_negative_sign(self):
        self.assertEqual(self.locale.negative_sign, u'-')

    def test_positive_sign(self):
        self.assertEqual(self.locale.positive_sign, u'')
    
    def test_month_name(self):
        self.assertEqual(self.locale.month_name(1), u'January')
        self.assertEqual(self.locale.month_name(2), u'February')
        self.assertEqual(self.locale.month_name(3), u'March')
        self.assertEqual(self.locale.month_name(4), u'April')
        self.assertEqual(self.locale.month_name(5), u'May')
        self.assertEqual(self.locale.month_name(6), u'June')
        self.assertEqual(self.locale.month_name(7), u'July')
        self.assertEqual(self.locale.month_name(8), u'August')
        self.assertEqual(self.locale.month_name(9), u'September')
        self.assertEqual(self.locale.month_name(10), u'October')
        self.assertEqual(self.locale.month_name(11), u'November')
        self.assertEqual(self.locale.month_name(12), u'December')

    def test_month_name_abbr(self):
        self.assertEqual(self.locale.month_name(1, abbreviated=True), u'Jan')
        self.assertEqual(self.locale.month_name(2, abbreviated=True), u'Feb')
        self.assertEqual(self.locale.month_name(3, abbreviated=True), u'Mar')
        self.assertEqual(self.locale.month_name(4, abbreviated=True), u'Apr')
        self.assertEqual(self.locale.month_name(5, abbreviated=True), u'May')
        self.assertEqual(self.locale.month_name(6, abbreviated=True), u'Jun')
        self.assertEqual(self.locale.month_name(7, abbreviated=True), u'Jul')
        self.assertEqual(self.locale.month_name(8, abbreviated=True), u'Aug')
        self.assertEqual(self.locale.month_name(9, abbreviated=True), u'Sep')
        self.assertEqual(self.locale.month_name(10, abbreviated=True), u'Oct')
        self.assertEqual(self.locale.month_name(11, abbreviated=True), u'Nov')
        self.assertEqual(self.locale.month_name(12, abbreviated=True), u'Dec')

    def test_day_name(self):
        self.assertEqual(self.locale.day_name(1), u'Sunday')
        self.assertEqual(self.locale.day_name(2), u'Monday')
        self.assertEqual(self.locale.day_name(3), u'Tuesday')
        self.assertEqual(self.locale.day_name(4), u'Wednesday')
        self.assertEqual(self.locale.day_name(5), u'Thursday')
        self.assertEqual(self.locale.day_name(6), u'Friday')
        self.assertEqual(self.locale.day_name(7), u'Saturday')

    def test_day_name_abbr(self):
        self.assertEqual(self.locale.day_name(1, abbreviated=True), u'Sun')
        self.assertEqual(self.locale.day_name(2, abbreviated=True), u'Mon')
        self.assertEqual(self.locale.day_name(3, abbreviated=True), u'Tue')
        self.assertEqual(self.locale.day_name(4, abbreviated=True), u'Wed')
        self.assertEqual(self.locale.day_name(5, abbreviated=True), u'Thu')
        self.assertEqual(self.locale.day_name(6, abbreviated=True), u'Fri')
        self.assertEqual(self.locale.day_name(7, abbreviated=True), u'Sat')

    def test_time_format(self):
        self.assertEqual(self.locale.time_format(), u'%I:%M:%S %p')
        self.assertEqual(self.locale.time_format(abbreviated=True), u'%H:%M:%S')

    def test_date_format(self):
        self.assertEqual(self.locale.date_format(), u'%m/%d/%Y')
        self.assertEqual(self.locale.date_format(abbreviated=True), u'%m/%d/%Y')

    def test_datetime_format(self):
        self.assertEqual(self.locale.datetime_format(), u'%a %b %d %X %Y')
        self.assertEqual(self.locale.datetime_format(abbreviated=True), u'%a %b %d %X %Y')

    def test_to_time(self):
        t1 = datetime.time(15, 27, 38)
        t2 = datetime.time(4, 19, 42)
        self.assertEqual(self.locale.to_time('3:27:38 PM'), t1)
        self.assertEqual(self.locale.to_time('15:27:38', abbreviated=True), t1)
        self.assertEqual(self.locale.to_time('4:19:42 AM'), t2)
        self.assertEqual(self.locale.to_time('4:19:42', abbreviated=True), t2)

    def test_from_time(self):
        t1 = datetime.time(15, 27, 38)
        t2 = datetime.time(4, 19, 42)
        self.assertEqual(self.locale.from_time(t1), u'03:27:38 PM')
        self.assertEqual(self.locale.from_time(t1, abbreviated=True), u'15:27:38')
        self.assertEqual(self.locale.from_time(t2), u'04:19:42 AM')
        self.assertEqual(self.locale.from_time(t2, abbreviated=True), u'04:19:42')

    def test_to_date(self):
        d1 = datetime.date(1943, 3, 28)
        d2 = datetime.date(2050, 12, 20)
        self.assertEqual(self.locale.to_date('3/28/1943'), d1)
        self.assertEqual(self.locale.to_date('3/28/1943', abbreviated=True), d1)
        self.assertEqual(self.locale.to_date('03/28/1943'), d1)
        self.assertEqual(self.locale.to_date('03/28/1943', abbreviated=True), d1)
        self.assertEqual(self.locale.to_date('12/20/2050'), d2)
        self.assertEqual(self.locale.to_date('12/20/2050', abbreviated=True), d2)

    def test_from_date(self):
        d1 = datetime.date(1943, 3, 28)
        d2 = datetime.date(2050, 12, 20)
        self.assertEqual(self.locale.from_date(d1), u'03/28/1943')
        self.assertEqual(self.locale.from_date(d1, abbreviated=True), u'03/28/1943')
        self.assertEqual(self.locale.from_date(d2), u'12/20/2050')
        self.assertEqual(self.locale.from_date(d2, abbreviated=True), u'12/20/2050')

    def test_to_datetime(self):
        d1 = datetime.datetime(1943, 3, 28, 15, 27, 38)
        d2 = datetime.datetime(2050, 12, 20, 4, 19, 42)
        self.assertEqual(self.locale.to_datetime('Sun Mar 28 15:27:38 1943'), d1)
        self.assertEqual(self.locale.to_datetime('Sun Mar 28 15:27:38 1943', abbreviated=True), d1)
        self.assertEqual(self.locale.to_datetime('Tue Dec 20 4:19:42 2050'), d2)
        self.assertEqual(self.locale.to_datetime('Tue Dec 20 4:19:42 2050', abbreviated=True), d2)

    def test_from_datetime(self):
        d1 = datetime.datetime(1943, 3, 28, 15, 27, 38)
        d2 = datetime.datetime(2050, 12, 20, 4, 19, 42)
        self.assertEqual(self.locale.from_datetime(d1), u'Sun Mar 28 15:27:38 1943')
        self.assertEqual(self.locale.from_datetime(d1, abbreviated=True), u'Sun Mar 28 15:27:38 1943')
        self.assertEqual(self.locale.from_datetime(d2), u'Tue Dec 20 04:19:42 2050')
        self.assertEqual(self.locale.from_datetime(d2, abbreviated=True), u'Tue Dec 20 04:19:42 2050')

    def test_to_int(self):
        self.assertEqual(self.locale.to_int('12'), 12)
        self.assertEqual(self.locale.to_int('12,345,678'), 12345678)
        self.assertEqual(self.locale.to_int('10', base=2), 2)
        self.assertEqual(self.locale.to_int('0B10', base=2), 2)
        self.assertEqual(self.locale.to_int('0b10', base=2), 2)
        self.assertEqual(self.locale.to_int('17', base=8), 15)
        self.assertEqual(self.locale.to_int('017', base=8), 15)
        self.assertEqual(self.locale.to_int('FF', base=16), 255)
        self.assertEqual(self.locale.to_int('ff', base=16), 255)
        self.assertEqual(self.locale.to_int('0XFF', base=16), 255)
        self.assertEqual(self.locale.to_int('0xFF', base=16), 255)
        self.assertEqual(self.locale.to_int('0Xff', base=16), 255)
        self.assertEqual(self.locale.to_int('0xff', base=16), 255)
        self.assertEqual(self.locale.to_int('456', base=17), 1247)
        self.assertEqual(self.locale.to_int('456', base=36), 5370)
        self.assertEqual(self.locale.to_int('456', base=7), 237)
        self.assertEqual(self.locale.to_int('12AZ', base=36), 49643)

    def test_from_int(self):
        self.assertEqual(self.locale.from_int(12), u'12')
        self.assertEqual(self.locale.from_int(12345678, group=True), u'12,345,678')
        self.assertEqual(self.locale.from_int(2, base=2), u'0b10')
        self.assertEqual(self.locale.from_int(15, base=8), u'017')
        self.assertEqual(self.locale.from_int(255, base=16), u'0XFF')
        self.assertEqual(self.locale.from_int(1247, base=17), '456')
        self.assertEqual(self.locale.from_int(5370, base=36), '456')
        self.assertEqual(self.locale.from_int(237, base=7), '456')
        self.assertEqual(self.locale.from_int(49643, base=36), '12AZ')

    def test_to_long(self):
        self.assertEqual(self.locale.to_long('12345678901'), 12345678901L)
        self.assertEqual(self.locale.to_long('12,345,678,901'), 12345678901L)
        self.assertEqual(self.locale.to_long('1'*32, base=2), 4294967295L)
        self.assertEqual(self.locale.to_long('0B' + '1'*32, base=2), 4294967295L)
        self.assertEqual(self.locale.to_long('0b' + '1'*32, base=2), 4294967295L)
        self.assertEqual(self.locale.to_long('1'*12, base=8), 9817068105L)
        self.assertEqual(self.locale.to_long('0' + '1'*12, base=8), 9817068105L)
        self.assertEqual(self.locale.to_long('F'*8, base=16), 4294967295L)
        self.assertEqual(self.locale.to_long('f'*8, base=16), 4294967295L)
        self.assertEqual(self.locale.to_long('0X' + 'F'*8, base=16), 4294967295L)
        self.assertEqual(self.locale.to_long('0X' + 'f'*8, base=16), 4294967295L)
        self.assertEqual(self.locale.to_long('0x' + 'F'*8, base=16), 4294967295L)
        self.assertEqual(self.locale.to_long('0x' + 'f'*8, base=16), 4294967295L)
        self.assertEqual(self.locale.to_long('456'*3, base=17), 30105676301L)
        self.assertEqual(self.locale.to_long('456'*3, base=36), 11689571692410L)
        self.assertEqual(self.locale.to_long('456'*4, base=7), 9591769200L)

    def test_from_long(self):
        self.assertEqual(self.locale.from_long(12L), u'12')
        self.assertEqual(self.locale.from_long(12345678L, group=True), u'12,345,678')
        self.assertEqual(self.locale.from_long(2L, base=2), u'0b10')
        self.assertEqual(self.locale.from_long(15L, base=8), u'017')
        self.assertEqual(self.locale.from_long(255L, base=16), u'0XFF')
        self.assertEqual(self.locale.from_long(1247L, base=17), u'456')
        self.assertEqual(self.locale.from_long(5370L, base=36), u'456')
        self.assertEqual(self.locale.from_long(237L, base=7), u'456')
        self.assertEqual(self.locale.from_long(49643L, base=36), u'12AZ')

    def test_to_float(self):
        self.assertAlmostEqual(self.locale.to_float('12'), 12.0)
        self.assertAlmostEqual(self.locale.to_float('12.42'), 12.42)
        self.assertAlmostEqual(self.locale.to_float('12,345,644.23'), 12345644.23)
        self.assertAlmostEqual(self.locale.to_float('12345644.23'), 12345644.23)
        self.assertAlmostEqual(self.locale.to_float('0.0000123'), 0.0000123)
        self.assertAlmostEqual(self.locale.to_float('123.45678'), 123.45678)
        self.assertAlmostEqual(self.locale.to_float('123e-4'), 123e-4)
        self.assertAlmostEqual(self.locale.to_float('123E-4'), 123e-4)
    
    def test_from_float(self):
        self.assertEqual(self.locale.from_float(12.0), u'12')
        self.assertEqual(self.locale.from_float(12.42), u'12.42')
        self.assertEqual(self.locale.from_float(12345644.23), u'1.23456e+07')
        self.assertEqual(self.locale.from_float(12345644.23, prec=10), u'12345644.23')
        self.assertEqual(self.locale.from_float(12345644.23, group=True, prec=10), u'12,345,644.23')
        self.assertEqual(self.locale.from_float(0.0000123), u'1.23e-05')
        self.assertEqual(self.locale.from_float(0.00123), u'0.00123')
        self.assertEqual(self.locale.from_float(123.456), u'123.456')
        self.assertEqual(self.locale.from_float(123e-4), u'0.0123')

    def test_to_complex(self):
        self.assertAlmostEqual(self.locale.to_complex('12'), complex(12))
        self.assertAlmostEqual(self.locale.to_complex('12.5'), complex(12.5))
        self.assertAlmostEqual(self.locale.to_complex('12.5j'), 12.5j)
        self.assertAlmostEqual(self.locale.to_complex('12.3+12.4j'), 12.3+12.4j)
        self.assertAlmostEqual(self.locale.to_complex('11.4-6.32j'), 11.4-6.32j)
        self.assertAlmostEqual(self.locale.to_complex('-3-5j'), -3-5j)
    
    def test_from_complex(self):
        self.assertEqual(self.locale.from_complex(12), u'12+0j')
        self.assertEqual(self.locale.from_complex(complex(12.5)), u'12.5+0j')
        self.assertEqual(self.locale.from_complex(12.5j), u'0+12.5j')
        self.assertEqual(self.locale.from_complex(12.3+12.4j), u'12.3+12.4j')
        self.assertEqual(self.locale.from_complex(11.4-6.32j), u'11.4-6.32j')
        self.assertEqual(self.locale.from_complex(-3-5j), u'-3-5j')

    def test_to_currency(self):
        self.assertAlmostEqual(self.locale.to_currency('$4.56'), 4.56)
        self.assertAlmostEqual(self.locale.to_currency('USD 4.56', intl=True), 4.56)
        self.assertAlmostEqual(self.locale.to_currency('$123456.45'), 123456.45) 
        self.assertAlmostEqual(self.locale.to_currency('$123,456.45', group=True), 123456.45)
        self.assertAlmostEqual(self.locale.to_currency('123,456.45', symbol=False, group=True), 123456.45)

    def test_from_currency(self):
        self.assertEqual(self.locale.from_currency(4.56), u'$4.56')
        self.assertEqual(self.locale.from_currency(4.56, intl=True), u'USD 4.56')
        self.assertEqual(self.locale.from_currency(123456.45), u'$123456.45') 
        self.assertEqual(self.locale.from_currency(123456.45, group=True), u'$123,456.45')
        self.assertEqual(self.locale.from_currency(123456.45, symbol=False, group=True), u'123,456.45')        

