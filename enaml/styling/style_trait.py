#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import TraitType

from .style_sheet import BoxedValue, StyleValue


NO_VALUE = object()


class _UserValue(BoxedValue):
    pass


class _DefaultValue(BoxedValue):
    pass


class StyleTrait(TraitType):

    def __init__(self, default_value=NO_VALUE, factory=None, **metadata):
        super(StyleTrait, self).__init__(**metadata)
        self._default_value_kw = default_value
        self._factory = factory

    def get(self, obj, name):
        attr = '_style_' + name
        try:
            boxed = obj.__dict__[attr]
        except KeyError:
            boxed = _DefaultValue(self._default_value(obj, name))
            obj.__dict__[attr] = boxed
        return boxed.value        

    def set(self, obj, name, value):
        # If we are being set with a StyleValue, then we only allow
        # the setting to occur if the current value is not a _UserValue
        attr = '_style_' + name
        try:
            old_boxed = obj.__dict__[attr]
        except KeyError:
            old_boxed = None
            old_value = NO_VALUE
        else:
            old_value = old_boxed.value

        if isinstance(value, StyleValue):
            if old_boxed is not None and isinstance(old_boxed, _UserValue):
                return
            box_type = StyleValue
            new_value = value.value
        else:
            box_type = _UserValue
            new_value = value

        new_value = self.convert(obj, name, new_value)
        new_boxed = box_type(new_value)        
        obj.__dict__[attr] = new_boxed
        if new_value != old_value:
            obj.trait_property_changed(name, old_value, new_value)

    def _default_value(self, obj, name):
        dv = self._default_value_kw
        if dv is not NO_VALUE:
            return dv
        
        factory = self._factory
        if factory is not None:
            return factory(obj, name)
        
        try:
            return self.create_default(obj, name)
        except NotImplementedError:
            pass

        msg = 'Cannot create a default value for %s' % name 
        raise ValueError(msg)
    
    def create_default(self, obj, name):
        raise NotImplementedError

    def convert(self, obj, name, value):
        raise NotImplementedError

