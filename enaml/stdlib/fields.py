#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------

from .converters import IntConverter, FloatConverter

defn ErrorField:
    error_color = '#F9A7A7'
    bg_color << error_color if error else "none"

defn IntField:
    ErrorField:
        converter = IntConverter
        #alignment = 'right'

defn LongField:
    ErrorField:
        converter = LongConverter
        #alignment = 'right'

defn FloatField:
    ErrorField:
        converter = FloatConverter
        #alignment = 'right'

defn ComplexField:
    ErrorField:
        converter = ComplexConverter
        #alignment = 'right'

defn PasswordField:
    Field:
        password_mode = 'password'
