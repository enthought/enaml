from .i_component import IComponent


class IElement(IComponent):
    """ The base class of all concretes widgets in TraitsML.

    Elements do not contain children and can be thought of 
    as terminal widgets in the TraitsML object tree.

    layout(parent)
        Initialize and layout the widget.

    """
    def layout(self, parent):
        """ Initialize and layout the widget.

        This method should be called by the parent window during
        its layout process.

        Arguments
        ---------
        parent : IContainer
            The parent container of this widget. The parent should 
            have already been layed out (and therefore have created 
            its internal widget) before being passed in to this method.

        Returns
        -------
        result : None

        Raises
        ------
        LayoutError
            Any reason the action cannot be completed.

        """
        raise NotImplementedError

