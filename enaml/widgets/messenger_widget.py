#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from enaml.core.declarative import Declarative
from enaml.utils import id_generator


class MessengerWidget(Declarative):
    """ The base class of all widget classes in Enaml.

    This extends Declarative with the ability to send and receive
    commands to and from a client.

    """
    #: The object id generator for widgets.
    object_id_generator = id_generator('w_')

