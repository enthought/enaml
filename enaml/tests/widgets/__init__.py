""" Toolkit independet abstract testing classes

The test.common package contains a set of abstract classes that homogenise
and simplify the testing of the Enaml object for the implemented toolkits.

All Enaml testcases are children of the :class:`EnamlTestCase` class.
The class implements the main functionality to parse and prepare
the Enaml-based View object for testing without initiating the event Loop.

For each Enaml object in the standard set of graphical widgets there exist
a corresponding abstract test class that tests the specific Enaml object
for conformance against the expected interface and behaviour. Each of them
require a set of methods (as described in the class docstring) to be
defined before the class can be created.


"""
