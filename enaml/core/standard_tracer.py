#------------------------------------------------------------------------------
#  Copyright (c) 2013, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import HasTraits, TraitListObject, TraitDictObject, Disallow
from atom.api import Atom

from .code_tracing import CodeTracer
from .dynamic_scope import AbstractScopeListener


class StandardTracer(CodeTracer):
    """ A CodeTracer for tracing expressions which use Traits.

    This tracer maintains a running set of `traced_items` which are the
    (obj, name) pairs of traits items discovered during tracing.

    """
    __slots__ = 'traced_items'

    def __init__(self):
        """ Initialize a TraitsTracer.

        """
        self.traced_items = set()

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _trace_trait(self, obj, name):
        """ Add the trait object and name pair to the traced items.

        Parameters
        ----------
        obj : HasTraits
            The traits object owning the attribute.

        name : str
            The trait name to for which to bind a handler.

        """
        # Traits will happily force create a trait for things which aren't
        # actually traits. This tries to avoid most of that when possible.
        trait = obj.trait(name)
        if trait is not None and trait.trait_type is not Disallow:
            self.traced_items.add((obj, name))

    def _trace_atom(self, obj, name):
        member = obj.lookup_member(name)
        if member is not None:
            self.traced_items.add((obj, name))

    #--------------------------------------------------------------------------
    # AbstractScopeListener Interface
    #--------------------------------------------------------------------------
    def dynamic_load(self, obj, attr, value):
        """ Called when an object attribute is dynamically loaded.

        This will trace the object if it is a HasTraits instance.
        See also: `AbstractScopeListener.dynamic_load`.

        """
        if isinstance(obj, HasTraits):
            self._trace_trait(obj, attr)
        elif isinstance(obj, Atom):
            self._trace_atom(obj, attr)

    #--------------------------------------------------------------------------
    # CodeTracer Interface
    #--------------------------------------------------------------------------
    def load_attr(self, obj, attr):
        """ Called before the LOAD_ATTR opcode is executed.

        This will trace the object if it is a HasTraits instance.
        See also: `CodeTracer.dynamic_load`.

        """
        if isinstance(obj, HasTraits):
            self._trace_trait(obj, attr)
        elif isinstance(obj, Atom):
            self._trace_atom(obj, attr)

    def call_function(self, func, argtuple, argspec):
        """ Called before the CALL_FUNCTION opcode is executed.

        This will trace the func is the builtin `getattr` and the object
        is a HasTraits instance. See also: `CodeTracer.call_function`

        """
        nargs = argspec & 0xFF
        nkwargs = (argspec >> 8) & 0xFF
        if (func is getattr and (nargs == 2 or nargs == 3) and nkwargs == 0):
            obj, attr = argtuple[0], argtuple[1]
            if isinstance(obj, HasTraits) and isinstance(attr, basestring):
                self._trace_trait(obj, attr)

    def binary_subscr(self, obj, idx):
        """ Called before the BINARY_SUBSCR opcode is executed.

        This will trace the object if it is a `TraitListObject` or a
        `TraitDictObject`. See also: `CodeTracer.get_iter`.

        """
        if isinstance(obj, (TraitListObject, TraitDictObject)):
            traits_obj = obj.object()
            if traits_obj is not None:
                if obj.name_items:
                    self._trace_trait(traits_obj, obj.name_items)

    def get_iter(self, obj):
        """ Called before the GET_ITER opcode is executed.

        This will trace the object if it is a `TraitListObject`
        See also: `CodeTracer.get_iter`.

        """
        if isinstance(obj, TraitListObject):
            traits_obj = obj.object()
            if traits_obj is not None:
                if obj.name_items:
                    self._trace_trait(traits_obj, obj.name_items)


AbstractScopeListener.register(StandardTracer)

