#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from __future__ import absolute_import

import unittest
import cPickle

from ..layout import geometry


class TestPickleGeometry(unittest.TestCase):
    def check_pickling(self, cls, nargs):
        args = (0,) * nargs
        obj = cls(*args)
        pickled = cPickle.dumps(obj, protocol=cPickle.HIGHEST_PROTOCOL)
        unpickled = cPickle.loads(pickled)
        self.assertEqual(obj, unpickled)

    def test_base_rect(self):
        self.check_pickling(geometry.BaseRect, 4)

    def test_rect(self):
        self.check_pickling(geometry.Rect, 4)

    def test_rect_f(self):
        self.check_pickling(geometry.RectF, 4)

    def test_base_box(self):
        self.check_pickling(geometry.BaseBox, 4)

    def test_box(self):
        self.check_pickling(geometry.Box, 4)

    def test_box_f(self):
        self.check_pickling(geometry.BoxF, 4)

    def test_base_pos(self):
        self.check_pickling(geometry.BasePos, 2)

    def test_pos(self):
        self.check_pickling(geometry.Pos, 2)

    def test_pos_f(self):
        self.check_pickling(geometry.PosF, 2)

    def test_base_size(self):
        self.check_pickling(geometry.BaseSize, 2)

    def test_size(self):
        self.check_pickling(geometry.Size, 2)

    def test_size_f(self):
        self.check_pickling(geometry.SizeF, 2)

