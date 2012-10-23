#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import warnings


warnings.warn(
    'Importing from enaml.core.signaling is deprectated. '
    'Use enaml.signaling instead.', DeprecationWarning
)

# Backwards compatibility imports
from enaml.signaling import Signal, BoundSignal as InstanceSignal

