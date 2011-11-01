from abc import ABCMeta, abstractmethod

from .symbolics import MultiConstraint, LinearSymbolic

from ..component import Component


# XXX make default space computed better
DEFAULT_SPACE = 10


#------------------------------------------------------------------------------
# Symbolic Constraint Factories
#------------------------------------------------------------------------------
class AbstractCnFactory(object):
    """ An abstract constraint factory class. This class is not meant to
    be used directly, but should be subclassed an have it 'constraint'
    method implement which will return a symbolics.LinearConstraint
    instance.

    """
    __metaclass__ = ABCMeta

    @staticmethod
    def validate(items):
        """ A validator staticmethod that insures a sequence of items is 
        appropriate for generating a sequence of linear constraints. The 
        following conditions are verfied of the sequence of given items:

            * There are two or more items in the sequence.

            * The first and last items are instances of either
              LinearSymbolic or Component.

            * All of the items in the sequence are instances of 
              LinearSymbolic, Component, Spacer, or int.
    
        If any of the above conditions do not hold, an exception is 
        raised with a (hopefully) useful error message.

        """
        if len(items) < 2:
            msg = 'Two or more items required to setup abutment constraints.'
            raise ValueError(msg)
        
        extrema_types = (LinearSymbolic, Component)
        def extrema_test(item):
            return isinstance(item, extrema_types)
        
        item_types = (LinearSymbolic, Component, BaseSpacer, int)
        def item_test(item):
            return isinstance(item, item_types)

        if not all(extrema_test(item) for item in (items[0], items[-1])):
            msg = ('The first and last items of an abutment constraint '
                   'sequence must be anchors or Components. Got %s')
            args = [type(items[0]), type(items[1])]
            raise TypeError(msg % args)
        
        if not all(map(item_test, items)):
            msg = ('The allowed items for an abutment constraint sequence '
                   'are anchors, Components, BaseSpacers, and ints. Got %s')
            args = [type(item) for item in items]
            raise TypeError(msg % args)

    @abstractmethod
    def constraint(self):
        """ An abstract method which must be implemented by subclasses.
        It should return an instance of symbolics.LinearConstraint.

        """
        raise NotImplementedError


class BaseCnFactory(AbstractCnFactory):
    """ A base constraint factory class that implements some
    basic common logic. It is not meant to be used directly but
    should rather be subclassed to be useful.

    """
    def __init__(self, first_anchor, spacer, second_anchor):
        """ Create an base constraint instance.

        Parameters
        ----------
        first_anchor : LinearSymbolic
            A symbolic object that can be used in a constraint expression.
        
        spacer : BaseSpacer
            A spacer instance to put space between the items.
        
        second_anchor : LinearSymbolic
            The second anchor for the constraint expression.


        """
        self.first_anchor = first_anchor
        self.spacer = spacer
        self.second_anchor = second_anchor

    def constraint(self):
        """ Returns a LinearConstraint instance which is formed through
        an appropriate linear expression for the given space between 
        the anchors.

        """
        return self.spacer.constrain(self.first_anchor, self.second_anchor)


class AbutmentCn(BaseCnFactory):
    """ A CnFactory subclass that represents an abutment constraint, 
    which is a constraint between two anchors of different components
    separated by some amount of space. It provides a 'from_items'
    classmethod which will create a sequence of abutment constraints
    from a sequence of items and a direction.

    """
    #: A mapping from direction to the order of anchor names to 
    #: lookup for a pair of items in order to make the constraint.
    direction_map = {
        'horizontal': ('right', 'left'),
        'vertical': ('bottom', 'top'),
    }

    @classmethod
    def from_items(cls, items, direction):
        """ A classmethod that will create a seqence of abutment 
        constraints given a sequence of items and a direction. The 
        direction must be 'horizontal' or 'vertical'. The order of
        abutment is left-to-right for horizontal direction and 
        top-to-bottom for vertical direction.

        """
        # Make sure the items we'll be dealing with are valid
        # for the algorithm. This is a basic validation. Further
        # error handling is done the _handle_item method.
        cls.validate(items)

        # Grab the tuple of anchor names to lookup for each 
        # pair of items in order to make the connection.
        first_name, second_name = cls.direction_map[direction]
    
        # The list of constraints we'll be creating for the
        # given sequence of items.
        cns = []

        # The list of items is treated as a stack. So we want
        # to first reverse it so the first items are at the top
        # of the stack.
        items = list(reversed(items))

        while items:
            # Grab the item that will provide the first anchor in
            # constraint pair
            first_item = items.pop()

            # first_item will be either a Component or a LinearSymbolic.
            # For the first iteration, this is enfored by the staticmethod
            # 'validate'. For subsequent iterations, this condition is 
            # enforced by the fact that this loop only pushes those types 
            # back onto the stack.
            if isinstance(first_item, Component):
                first_anchor = getattr(first_item, first_name)
            elif isinstance(first_item, LinearSymbolic):
                first_anchor = first_item
            else:
                raise TypeError('This should never happen')
            
            # Grab the next item off the stack. It is either a 
            # Component, LinearSymbolic, Spacer, or int. If it
            # can't provide an anchor, we grab the after that
            # which *should* be able to provide one. If no space
            # is given, we compute a default space.
            next_item = items.pop()
            if isinstance(next_item, BaseSpacer):
                spacer = next_item
                second_item = items.pop()
            elif isinstance(next_item, int):
                spacer = EqSpacer(next_item)
                second_item = items.pop()
            elif isinstance(next_item, Component):
                spacer = EqSpacer()
                second_item = next_item
            elif isinstance(next_item, LinearSymbolic):
                spacer = EqSpacer()
                second_item = next_item
            else:
                raise ValueError('This should never happen')
            
            # If the second_item can't provide an anchor, such as
            # two spacers next to each other, then this is an error
            # condition and we raise an appropriate exception.
            if isinstance(second_item, Component):
                second_anchor = getattr(second_item, second_name)   
            elif isinstance(second_item, LinearSymbolic):
                second_anchor = second_item
            else:
                msg = 'Expected anchor or Component. Got %s instead.'
                raise TypeError(msg % second_item)
            
            # Create the class instance for this constraint
            factory = cls(first_anchor, spacer, second_anchor)

            # If there are still items on the stack, then the second_item
            # will be used as the first_item in the next iteration. 
            # Otherwise, we have exhausted all constraints and can 
            # exit the loop.
            if items:
                items.append(second_item)

            # Finally, store away the created constraint to return
            # to the caller.
            cns.append(factory)

        return cns


class AlignmentCn(BaseCnFactory):
    """ A CnFactory subclass that represents an alignmnent constraint, 
    which is a constraint between two anchors of different components
    which are aligned but may be separated by some amount of space.
    It provides a 'from_items' classmethod which will create a sequence 
    of alignment constraints from a sequence of items and an anchor name.

    """
    @classmethod
    def from_items(cls, items, anchor_name):
        """ A classmethod that will create a seqence of alignment
        constraints given a sequence of items and an anchor name. The 
        anchor name must be 'left', 'right', 'top', 'bottom', 'v_center',
        or 'h_center'. For every item in the sequence, if the item is a
        component, then anchor for the given anchor_name on that component
        will be used. If a LinearSymbolic is given, then that symbolic
        will be used and the anchor_name will be ignored. Specifying space
        between items is allowed.

        """
        # Make sure the items we'll be dealing with are valid
        # for the algorithm. This is a basic validation. Further
        # error handling is done the _handle_item method.
        cls.validate(items)

        # The list of constraints we'll be creating for the
        # given sequence of items.
        cns = []

        # The list of items is treated as a stack. So we want
        # to first reverse it so the first items are at the top
        # of the stack.
        items = list(reversed(items))

        while items:
            # Grab the item that will provide the first anchor in
            # constraint pair
            first_item = items.pop()

            # first_item will be either a Component or a LinearSymbolic.
            # For the first iteration, this is enfored by the staticmethod
            # 'validate'. For subsequent iterations, this condition is 
            # enforced by the fact that this loop only pushes those types 
            # back onto the stack.
            if isinstance(first_item, Component):
                first_anchor = getattr(first_item, anchor_name)
            elif isinstance(first_item, LinearSymbolic):
                first_anchor = first_item
            else:
                raise TypeError('This should never happen')
            
            # Grab the next item off the stack. It is either a 
            # Component, LinearSymbolic, Spacer, or int. If it
            # can't provide an anchor, we grab the after that
            # which *should* be able to provide one. If no space
            # is given, we compute a default space of zero since
            # that is what is typically wanted out of an alignment.
            item = items.pop()
            if isinstance(item, BaseSpacer):
                spacer = item
                second_item = items.pop()
            elif isinstance(item, int):
                spacer = EqSpacer(item)
                second_item = items.pop()
            elif isinstance(item, Component):
                spacer = EqSpacer(0)
                second_item = item
            elif isinstance(item, LinearSymbolic):
                spacer = EqSpacer(0)
                second_item = item
            else:
                raise ValueError('This should never happen')
            
            # If the second_item can't provide an anchor, such as
            # two spacers next to each other, then this is an error
            # condition and we raise an appropriate exception.
            if isinstance(second_item, Component):
                second_anchor = getattr(second_item, anchor_name)   
            elif isinstance(second_item, LinearSymbolic):
                second_anchor = second_item
            else:
                msg = 'Invalid object for second abutment constraint: %s'
                raise TypeError(msg % second_item)

            # Create the class instance for this constraint
            factory = cls(first_anchor, spacer, second_anchor)

            # If there are still items on the stack, then the second_item
            # will be used as the first_item in the next iteration. 
            # Otherwise, we have exhausted all constraints and can 
            # exit the loop.
            if items:
                items.append(second_item)

            # Finally, store away the created constraint to return
            # to the caller.
            cns.append(factory)

        return cns


#------------------------------------------------------------------------------
# Spacers
#------------------------------------------------------------------------------
class BaseSpacer(object):
    """ An abstract base spacer class. Subclasses must implement the
    'constrain' method.

    """
    __metaclass__ = ABCMeta

    __slots__ = ()

    @abstractmethod
    def constrain(self, first_anchor, second_anchor):
        """ An abstract method. Subclasses should implement this 
        method to return a symbolics.LinearConstraint object that
        is appropriate to separate the two anchors according to
        the amount of space represented by the spacer.

        """
        raise NotImplementedError


class Spacer(BaseSpacer):
    """ A spacer base class which adds support for storing a value
    which represent the amount of space to use in the constraint.

    """
    __slots__ = ('amt',)

    def __init__(self, amt=DEFAULT_SPACE):
        self.amt = max(0, amt)


class EqSpacer(Spacer):
    """ An spacer which represents a fixed amount of space.

    """
    __slots__ = ()

    def constrain(self, first_anchor, second_anchor):
        """ A constraint of the form (anchor_1 + space == anchor_2)

        """
        return first_anchor + self.amt == second_anchor


class LeSpacer(Spacer):
    """ A spacer which represents a flexible space with a maximum value.

    """
    __slots__ = ()

    def constrain(self, first_anchor, second_anchor):
        """ A constraint of the form (anchor_1 + space >= anchor_2)
        That is, the visible space must be less than or equal to the
        given amount.

        """
        return first_anchor + self.amt >= second_anchor


class GeSpacer(Spacer):
    """ A spacer which represents a flexible space with a minimum value.

    """
    __slots__ = ()

    def constrain(self, first_anchor, second_anchor):
        """ A constraint of the form (anchor_1 + space >= anchor_2)
        That is, the visible space must be greater than or equal to
        the given amount.

        """
        return first_anchor + self.amt <= second_anchor


class _space_(BaseSpacer):
    """ A special singleton symbolic, spacer that, alone, represents a 
    flexible space with a minimum value of the default space, but can be 
    combined with the ==, <=, and >= operators to create different types 
    of space.

    """
    __slots__ = ()

    def __eq__(self, other):
        if not isinstance(other, int):
            raise TypeError('space can only be created from ints')
        return EqSpacer(other)
    
    def __le__(self, other):
        if not isinstance(other, int):
            raise TypeError('space can only be created from ints')
        return LeSpacer(other)
    
    def __ge__(self, other):
        if not isinstance(other, int):
            raise TypeError('space can only be created from ints')
        return GeSpacer(other)
    
    def constrain(self, first_anchor, second_anchor):
        """ Returns a constraint that is a flexible amount of space
        with a minimum equal to the default system space.

        """
        return GeSpacer().constrain(first_anchor, second_anchor)


# The singleton _space_ instance. There is no need for more than one.
_space_ = _space_()


#------------------------------------------------------------------------------
# Layout factory functions
#------------------------------------------------------------------------------
def horizontal(*items):
    """ Create a MutliConstraint object composed of horizontal abutments
    for the given sequence of items.

    """
    cns = [f.constraint() for f in AbutmentCn.from_items(items, 'horizontal')]
    return MultiConstraint(cns)


def vertical(*items):
    """ Create a MutliConstraint object composed of vertical abutments
    for the given sequence of items.

    """
    cns = [f.constraint() for f in AbutmentCn.from_items(items, 'vertical')]
    return MultiConstraint(cns)


def align_left(*items):
    """ Align the left anchors of the given components. Inter-component
    spacing is allowed.

    """
    cns = [f.constraint() for f in AlignmentCn.from_items(items, 'left')]
    return MultiConstraint(cns)


def align_right(*items):
    """ Align the right anchors of the given components. Inter-component
    spacing is allowed.
    
    """
    cns = [f.constraint() for f in AlignmentCn.from_items(items, 'right')]
    return MultiConstraint(cns)


def align_top(*items):
    """ Align the top anchors of the given components. Inter-component
    spacing is allowed.
    
    """
    cns = [f.constraint() for f in AlignmentCn.from_items(items, 'top')]
    return MultiConstraint(cns)


def align_bottom(*items):
    """ Align the bottom anchors of the given components. Inter-component
    spacing is allowed.
    
    """
    cns = [f.constraint() for f in AlignmentCn.from_items(items, 'bottom')]
    return MultiConstraint(cns)


def align_v_center(*items):
    """ Align the v_center anchors of the given components. Inter-component
    spacing is allowed.
    
    """
    cns = [f.constraint() for f in AlignmentCn.from_items(items, 'v_center')]
    return MultiConstraint(cns)


def align_h_center(*items):
    """ Align the h_center anchors of the given components. Inter-component
    spacing is allowed.
    
    """
    cns = [f.constraint() for f in AlignmentCn.from_items(items, 'h_center')]
    return MultiConstraint(cns)


#------------------------------------------------------------------------------
# Toolkit items
#------------------------------------------------------------------------------
LAYOUT_HELPERS = {
    'horizontal': horizontal,
    'vertical': vertical,
    'align_left': align_left,
    'align_right': align_right,
    'align_top': align_top,
    'align_bottom': align_bottom,
    'align_v_center': align_v_center,
    'align_h_center': align_h_center,
    '_space_': _space_,
}

