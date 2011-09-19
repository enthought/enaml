from .container import IContainerImpl, Container, Instance


class IFormImpl(IContainerImpl):
    pass


class Form(Container):
    """ A container that lays out its children as a form.

    The Form container arranges its children in N rows and 2 columns, 
    where the first column contains labels created from the name of
    the components.

    """
    #---------------------------------------------------------------------------
    # Overridden parent class traits
    #---------------------------------------------------------------------------
    toolkit_impl = Instance(IFormImpl)

