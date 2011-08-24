from traits.api import Interface


class IInterceptorFactory(Interface):
    """ Interface for interceptor factory objects.

    The IInterceptorFactory defines the interface for creating factories
    that create IInterceptor objects which bind code and/or expressions 
    to the TraitsML object tree.

    Methods
    -------
    interceptor()
        Creates an ITraitInterceptor instance that is primed for 
        injection into a HasTraits object.

    """
    def interceptor(self):
        """ Creates an ITraitInterceptor instance.

        Creates an ITraitInterceptor instance that is primed for 
        injection into a HasTraits object.

        Arguments
        ---------
        None

        Returns
        -------
        result : ITraitInterceptor
            The interceptor that will handle this code.

        Raises
        ------
        XXX

        """
        raise NotImplementedError

