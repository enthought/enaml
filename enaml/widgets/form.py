#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import on_trait_change

from .container import IContainerImpl, Container, Instance


class IFormImpl(IContainerImpl):
    
    def child_name_updated(self, child, name):
        raise NotImplementedError


class Form(Container):
    """ A container that lays out its children as a form.

    The Form container arranges its children in N rows and 2 columns, 
    where the first column contains labels created from the name of
    the components.

    """
    @on_trait_change('children:name')
    def child_name_update(self, obj, name, old, new):
        self.toolkit_impl.child_name_updated(obj, new)
        
    #---------------------------------------------------------------------------
    # Overridden parent class traits
    #---------------------------------------------------------------------------
    toolkit_impl = Instance(IFormImpl)

