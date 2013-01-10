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

        for good_val in good_values:
            comp.hug_width = good_val
            comp.hug_height = good_val
            self.assertEqual(comp.hug_width, good_val)
            self.assertEqual(comp.hug_height, good_val)

        for bad_val in bad_values:
            self.assertRaises(TraitError, comp.trait_set, hug_width=bad_val)
            self.assertRaises(TraitError, comp.trait_set, hug_height=bad_val)

    def test_resist_clip_property(self):
        """ Test that the resist_clip property works correctly.

        """
        good_values = ['ignore', 'weak', 'medium', 'strong', 'required']
        bad_values = ['Ignore', None, 'srong']

        comp = ConstraintsWidget()

        for good_val in good_values:
            comp.resist_width = good_val
            comp.resist_height = good_val
            self.assertEqual(comp.resist_width, good_val)
            self.assertEqual(comp.resist_height, good_val)

        for bad_val in bad_values:
            self.assertRaises(TraitError, comp.trait_set, resist_width=bad_val)
            self.assertRaises(TraitError, comp.trait_set, resist_height=bad_val)

