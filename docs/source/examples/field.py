#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import enaml

with enaml.imports():
    from field import FieldExample

view = FieldExample()
view.show()
