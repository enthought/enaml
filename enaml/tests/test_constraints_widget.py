#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from unittest import TestCase

from traits.api import TraitError

from ..widgets.constraints_widget import ConstraintsWidget


class TestLayoutComponent(TestCase):
    """ Test basic operations on LayoutComponents.

    """
    def test_hug_property(self):
        """ Test that the hug property works correctly.

        """
        good_values = ['ignore', 'weak', 'medium', 'strong', 'required']
        bad_values = ['Ignore', None, 'srong']

        comp = ConstraintsWidget()
        self.assertEqual(comp.hug_width, 'strong')
        self.assertEqual(comp.hug_height, 'strong')
        self.assertEqual(comp._layout_info()['hug'], ('strong', 'strong'))
        comp.hug_width = 'ignore'
        comp.hug_height = 'medium'
        self.assertEqual(comp._layout_info()['hug'], ('ignore', 'medium'))

        for good_width in good_values:
            for good_height in good_values:
                comp.hug_width = good_width
                comp.hug_height = good_height

        for bad_height in bad_values:
            self.assertRaises(TraitError, comp.trait_set, hug_height=bad_height)

        for bad_width in bad_values:
            self.assertRaises(TraitError, comp.trait_set, hug_width=bad_width)

    def test_resist_clip_property(self):
        """ Test that the resist_clip property works correctly.

        """
        good_values = ['ignore', 'weak', 'medium', 'strong', 'required']
        bad_values = ['Ignore', None, 'srong']

        comp = ConstraintsWidget()
        self.assertEqual(comp.resist_width, 'strong')
        self.assertEqual(comp.resist_height, 'strong')

        for value in good_values:
            comp.resist_width = value
            comp.resist_height = value

        for bad_height in bad_values:
            self.assertRaises(TraitError, comp.trait_set, resist_height=bad_height)

        for bad_width in bad_values:
            self.assertRaises(TraitError, comp.trait_set, resist_width=bad_width)

