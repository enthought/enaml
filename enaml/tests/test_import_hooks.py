#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import sys
import unittest

from enaml.core import import_hooks


class FakeSys(object):
    def __init__(self):
        self.meta_path = []


class TestImportHooks(unittest.TestCase):

    def setUp(self):
        # Monkey-patch "sys" in the import_hooks module.
        import_hooks.sys = FakeSys()

    def tearDown(self):
        import_hooks.sys = sys

    def test_install_count(self):
        """ Test that EnamlImporter can be installed in a nested manner.

        """
        importer = import_hooks.EnamlImporter
        counts = importer._install_count
        meta_path = import_hooks.sys.meta_path

        self.assertEquals(counts[importer], 0)
        self.assertEquals(len(meta_path), 0)

        importer.install()
        self.assertEquals(counts[importer], 1)
        self.assertEquals(len(meta_path), 1)

        importer.install()
        self.assertEquals(counts[importer], 2)
        self.assertEquals(len(meta_path), 1)

        importer.uninstall()
        self.assertEquals(counts[importer], 1)
        self.assertEquals(len(meta_path), 1)

        importer.uninstall()
        self.assertEquals(counts[importer], 0)
        self.assertEquals(len(meta_path), 0)

