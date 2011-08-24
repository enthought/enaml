from .i_container import IContainer


class IForm(IContainer):
    """ A container that lays out its children as a form.

    The Form container arranges its children in N rows and 2 cols.
    If there are an odd number of children, the last child will
    span both cols.

    """
    pass

