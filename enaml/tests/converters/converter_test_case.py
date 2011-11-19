#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import unittest


class ConverterTestCase(unittest.TestCase):
    """ A base class for testing `enaml.converters.Converter` objects.

    """
    def assertConverterSymmetric(self, converter, widget_value, external_value):
        """ Check that the 'to_component' and 'from_component' methods of
        a converter are symmetric:


        """
        external_converted = converter.from_component(widget_value)
        self.assertEqual(external_converted, external_value)

        widget_converted = converter.to_component(external_value)
        self.assertEqual(widget_converted, widget_value)

        # XXX Should we check the types?
