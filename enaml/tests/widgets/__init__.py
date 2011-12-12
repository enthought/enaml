#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
""" Toolkit independed abstract testing classes

The tests.widgets package contains a set of abstract classes that simplify
the testing of the Enaml object components for the implemented toolkits.

All Enaml testcases are children of the
:class:`~enaml.tests.widgets.enaml_test_case.EnamlTestCase` class. The
class implements the main functionality to parse and prepare the Enaml
based View object for testing without initiating the event Loop.

For each Enaml object in the standard set of graphical widgets there exist
a corresponding abstract test class that tests the specific Enaml object
for conformance against the expected interface and behaviour. Each of them
require a set of methods (as described in the class docstring) to be
defined before the class can be created.

"""
