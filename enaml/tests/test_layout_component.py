#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from unittest import TestCase

from traits.api import TraitError

from ..widgets.layout_component import LayoutComponent


class TestLayoutComponent(TestCase):
    """ Test basic operations on LayoutComponents.

    """
    def test_hug_property(self):
        """ Test that the hug property works correctly.

        """
        good_values = ['ignore', 'weak', 'medium', 'strong', 'required']
        bad_values = ['Ignore', None, 'srong']

        comp = LayoutComponent()
        self.assertEqual(comp.hug_width, 'strong')
        self.assertEqual(comp.hug_height, 'strong')
        self.assertEqual(comp.hug, ('strong', 'strong'))
        comp.hug_width = 'ignore'
        self.assertEqual(comp.hug, ('ignore', 'strong'))
        comp.hug_height = 'medium'
        self.assertEqual(comp.hug, ('ignore', 'medium'))
        comp.hug = ('weak', 'required')

        for good_width in good_values:
            for good_height in good_values:
                comp.hug = (good_width, good_height)
                self.assertEqual(comp.hug_width, good_width)
                self.assertEqual(comp.hug_height, good_height)

        for good_width in good_values:
            for bad_height in bad_values:
                self.assertRaises(TraitError, comp.trait_set, hug=(good_width, bad_height))

        for bad_width in good_values:
            for good_height in bad_values:
                self.assertRaises(TraitError, comp.trait_set, hug=(bad_width, good_height))

    def test_resist_clip_property(self):
        """ Test that the resist_clip property works correctly.

        """
        good_values = ['ignore', 'weak', 'medium', 'strong', 'required']
        bad_values = ['Ignore', None, 'srong']

        comp = LayoutComponent()
        self.assertEqual(comp.resist_clip_width, 'strong')
        self.assertEqual(comp.resist_clip_height, 'strong')
        self.assertEqual(comp.resist_clip, ('strong', 'strong'))
        comp.resist_clip_width = 'ignore'
        self.assertEqual(comp.resist_clip, ('ignore', 'strong'))
        comp.resist_clip_height = 'medium'
        self.assertEqual(comp.resist_clip, ('ignore', 'medium'))
        comp.resist_clip = ('weak', 'required')

        for good_width in good_values:
            for good_height in good_values:
                comp.resist_clip = (good_width, good_height)
                self.assertEqual(comp.resist_clip_width, good_width)
                self.assertEqual(comp.resist_clip_height, good_height)

        for good_width in good_values:
            for bad_height in bad_values:
                self.assertRaises(TraitError, comp.trait_set, resist_clip=(good_width, bad_height))

        for bad_width in good_values:
            for good_height in bad_values:
                self.assertRaises(TraitError, comp.trait_set, resist_clip=(bad_width, good_height))

