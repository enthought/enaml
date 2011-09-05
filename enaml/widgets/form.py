from .container import IContainerImpl, Container, Instance


class IFormImpl(IContainerImpl):
    pass


class Form(Container):
    """ A container that lays out its children as a form.

    The Form container arranges its children in N rows and 2 cols.
    If there are an odd number of children, the last child will
    span both cols.

    """
    #---------------------------------------------------------------------------
    # Overridden parent class traits
    #---------------------------------------------------------------------------
    toolkit_impl = Instance(IFormImpl)

