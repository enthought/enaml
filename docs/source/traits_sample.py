from traits.api import HasTraits, Float


class Myclass(HasTraits):
    """ This is a example class

    It is used to demonstrate the proposed guidelines for documenting traits
    based classes in an "sphinx-friendly" way.

    The traits are documented close to their definition by using a special
    comment `#:` prefix

    """

    #: The x Float trait (default = 150.0)
    x = Float(150.0)

    # This is a comment autodoc ignores it
    #: The y Float trait (default = 0.0)
    y = Float(0.0)

