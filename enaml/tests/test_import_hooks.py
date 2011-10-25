import sys
import unittest

from .. import import_hooks


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

        self.assertEquals(import_hooks.EnamlImporter.install_count, 0)
        self.assertEquals(len(import_hooks.sys.meta_path), 0)

        import_hooks.EnamlImporter.install()
        self.assertEquals(import_hooks.EnamlImporter.install_count, 1)
        self.assertEquals(len(import_hooks.sys.meta_path), 1)

        import_hooks.EnamlImporter.install()
        self.assertEquals(import_hooks.EnamlImporter.install_count, 2)
        self.assertEquals(len(import_hooks.sys.meta_path), 1)

        import_hooks.EnamlImporter.uninstall()
        self.assertEquals(import_hooks.EnamlImporter.install_count, 1)
        self.assertEquals(len(import_hooks.sys.meta_path), 1)

        import_hooks.EnamlImporter.uninstall()
        self.assertEquals(import_hooks.EnamlImporter.install_count, 0)
        self.assertEquals(len(import_hooks.sys.meta_path), 0)

