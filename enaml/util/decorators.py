

def protected(*names):
    """ Marks attributes with the given names as protected, so they cannot
    be delegated or have notifiers.

    """
    def closure(cls):
        try:
            protected = cls.__protected__
            protected.update(names)
        except AttributeError:
            protected = set(names)
        parent_cls = cls.mro()[1]
        try:
            parent_protected = parent_cls.__protected__
        except AttributeError:
            parent_protected = ()
        protected.update(parent_protected)
        cls.__protected__ = protected
        return cls
    return closure


def unprotect(*names):
    """ Marks attributes with the given names as unprotected, this is
    useful if a parent class has marked an attribute as protected and
    you want to undo that behavior.

    """
    def closure(cls):
        try:
            protected = cls.__protected__
        except:
            protected = set()
        parent_cls = cls.mro()[1]
        try:
            parent_protected = parent_cls.__protected__
        except AttributeError:
            parent_protected = ()
        protected.update(parent_protected)
        protected.difference_update(names)
        cls.__protected__ = protected
        return cls
    return closure

