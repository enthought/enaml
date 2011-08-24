from traits.api import Interface


class IInterceptorFactory(Interface):
    """ Interface for interceptor factory objects.

    The IInterceptorFactory defines the interface for creating factories
    that create IInterceptor objects which bind code and/or expressions 
    to the TraitsML object tree.

    Methods
    -------
    interceptor()
        Creates an IInterceptor instance that is primed for 
        injection into a HasTraits object.

    """
    def interceptor(self):
        """ Creates an IInterceptor instance.

        Creates an IInterceptor instance that is primed for 
        injection into a HasTraits object.

        Arguments
        ---------
        None

        Returns
        -------
        result : IInterceptor
            The interceptor that will handle this code.

        Raises
        ------
        XXX

        """
        raise NotImplementedError

