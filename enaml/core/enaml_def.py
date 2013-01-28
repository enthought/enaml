#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import MetaHasTraits


class EnamlDef(MetaHasTraits):
    """ The type of an enamldef.

    This is a metaclass used to create types for the 'enamldef' keyword.
    The metaclass assists with instantiating instances of these types
    and ensure they are properly populated using the description dicts
    created by the enaml compiler.

    """
    # Seed the class hierarchy with an empty descriptions tuple. The
    # compiler helper will add to this tuple when a new subclass is
    # created. The content will be 2-tuples of (description, globals)
    # which are the description dicts and the global scope for that
    # dict created by the enaml compiler.
    _descriptions = ()

    def __repr__(cls):
        """ A nice repr for a type created by the `enamldef` keyword.

        """
        return "<enamldef '%s.%s'>" % (cls.__module__, cls.__name__)

    def __call__(cls, parent=None, **kwargs):
        """ Create a new instance of a declarative type.

        This method ensures that the new instance is populated with the
        description dicts created by the enaml compiler. It also delays
        the application of any given keyword arguments until after the
        instance is fully populated.

        Parameters
        ----------
        parent : Declarative, optional
            The parent of the instance being created.

        **kwargs
            Additional keyword arguments to apply to the instance.

        Returns
        -------
        result : Declarative
            A new declarative instance for the given class.

        """
        # The only code that should be using this metaclass to create
        # classes is the compiler helper `_make_enamldef_helper_`. It
        # is therefore safe to assume `cls` is a Declarative subclass
        # and the new instances will behave appropriately.
        self = cls.__new__(cls)
        ob_type = type(self)
        if not issubclass(ob_type, cls):
            return self
        ob_type.__init__(self, parent=parent)
        descriptions = ob_type._descriptions
        if len(descriptions) > 0:
            with self.children_event_context():
                # Each description is an independent `enamldef` block
                # which gets its own independent identifiers scope.
                for description, f_globals in descriptions:
                    identifiers = {}
                    self.populate(description, identifiers, f_globals)
        if len(kwargs) > 0:
            for key, value in kwargs.iteritems():
                setattr(self, key, value)
        return self

