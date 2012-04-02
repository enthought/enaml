#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from abc import ABCMeta, abstractmethod

from traits.api import HasTraits, Range

from casuarius import ConstraintVariable, LinearSymbolic, Strength, STRENGTH_MAP

from .constrainable import Constrainable, PaddingConstraints
from .geometry import Box

from ..auxiliary.decorators import deprecated
from ..core.trait_types import CoercingInstance


#------------------------------------------------------------------------------
# Default Spacing
#------------------------------------------------------------------------------
class DefaultSpacing(HasTraits):
    """ A class which encapsulates the default spacing parameters for
    the various layout helper objects.

    """
    #: The space between abutted components
    ABUTMENT = Range(low=0, value=10)

    #: The space between aligned anchors
    ALIGNMENT = Range(low=0, value=0)

    #: The margins for box helpers
    BOX_MARGINS = CoercingInstance(Box, default=Box(0, 0, 0, 0))


# We only require a singleton of DefaultSpacing
DefaultSpacing = DefaultSpacing()


#------------------------------------------------------------------------------
# Abstract Constrainable Interface
#------------------------------------------------------------------------------
class ABConstrainable(object):
    """ Abstract base class for objects that can be laid out by these 
    helpers. Minimally, they need to have `top`, `bottom`, `left`, `right`
    attributes that are `LinearSymbolic` instances.

    """
    __metaclass__ = ABCMeta


ABConstrainable.register(Constrainable)


#------------------------------------------------------------------------------
# Helper Functions
#------------------------------------------------------------------------------
def expand_constraints(component, constraints):
    """ A function which expands any DeferredConstraints in the provided
    list. This is a generator function which yields the flattened stream 
    of constraints.

    Paramters
    ---------
    component : Constrainable
        The constrainable component with which the constraints are 
        associated. This will be passed to the .get_constraints() 
        method of any DeferredConstraint instance.
    
    constraints : list
        The list of constraints.
    
    Yields
    ------
    constraints
        The stream of expanded constraints.

    """
    for cn in constraints:
        if isinstance(cn, DeferredConstraints):
            for item in cn.get_constraints(component):
                if item is not None:
                    yield item
        else:
            if cn is not None:
                yield cn


def is_spacer(item):
    """ Returns True if the given item can be considered a spacer, False
    other otherwise.

    """
    return isinstance(item, (Spacer, int))


def is_really_visible(item):
    """ Returns True if the given item is actually visible on the screen.

    This is determined by checking all the ancestors of the component
    for visibility and only return True if they are all visible.

    """
    if not item.visible:
        return False
    for ancestor in item.traverse_ancestors():
        if not getattr(ancestor, 'visible', True):
            return False
    return True


def clear_invisible(items):
    """ Take a list of Components and other layout items and remove 
    logically invisible Components.

    This takes into account redundant spacer objects that may surround 
    invisible objects. Spacer objects that appear before an invisible 
    Component will be removed.

    Lists that consist solely of spacers will result in an empty list.

    Parameters
    ----------
    items : list
        The list of layout items to filter.
    
    Returns
    -------
    results : list
        A new list with logically invisible items removed.

    """
    vis = []
    push = vis.append
    pop = vis.pop
    for item in items:
        if isinstance(item, Constrainable) and not is_really_visible(item):
            if len(vis) > 0 and is_spacer(vis[-1]):
                pop()
        else:
            push(item)
    if all(is_spacer(item) for item in vis):
        vis = []
    return vis


#------------------------------------------------------------------------------
# Deferred Constraints
#------------------------------------------------------------------------------
class DeferredConstraints(object):
    """ Abstract base class for objects that will yield lists of 
    constraints upon request.

    """
    __metaclass__ = ABCMeta

    def __init__(self, *args, **kwds):
        """ Initialize a DeferredConstraints instance.

        """
        self.clear_invisible = kwds.get('clear_invisible', True)
        # __or__() will set these default strength and weight. If
        # provided, they will be combined with the constraints created
        # by this instance.
        self.default_strength = None
        self.default_weight = None

    def __or__(self, other):
        """ Set the strength of all of the constraints to a common 
        strength.

        """
        if isinstance(other, (float, int, long)):
            self.default_weight = float(other)
        elif isinstance(other, basestring):
            if other not in STRENGTH_MAP:
                raise ValueError('Invalid strength %r' % other)
            self.default_strength = STRENGTH_MAP[other]
        elif isinstance(other, Strength):
            self.default_strength = other
        else:
            msg = 'Strength must be a string. Got %s instead.'
            raise TypeError(msg % type(other))
        return self

    def when(self, switch):
        """ A simple method that can be used to switch off the generated
        constraints depending on a boolean value.

        """
        if switch:
            return self
    
    def get_constraints(self, component):
        """ Returns a list of weighted LinearConstraints.

        Parameters
        ----------
        component : Component or None
            The component that owns this DeferredConstraints. It can 
            be None for contexts in which there is not a containing
            component, such as in certain nested DeferredConstraints.

        Returns
        -------
        result : list of LinearConstraints
            The list of LinearConstraint objects which have been 
            weighted by any provided strengths and weights.
        
        """
        cn_list = self._get_constraints(component)
        strength = self.default_strength
        if strength is not None:
            cn_list = [cn | strength for cn in cn_list]
        weight = self.default_weight
        if weight is not None:
            cn_list = [cn | weight for cn in cn_list]
        return cn_list

    @abstractmethod
    def _get_constraints(self, component):
        """ Returns a list of LinearConstraint objects.

        Subclasses must implement this method to actually yield their
        constraints. Users of instances should instead call the 
        `get_weighted_constraints()` method which will combine these 
        constraints with the `default_strength` and/or the 
        `default_weight` if one or both are provided.

        Parameters
        ----------
        component : Component or None
            The component that owns this DeferredConstraints. It can 
            be None for contexts in which there is not a containing
            component, such as in certain nested DeferredConstraints.

        Returns
        -------
        result : list of LinearConstraints
            The list of LinearConstraint objects for this deferred 
            instance.

        """
        raise NotImplementedError


#------------------------------------------------------------------------------
# Deferred Constraints Implementations
#------------------------------------------------------------------------------
class DeferredConstraintsFunction(DeferredConstraints):
    """ A concrete implementation of DeferredConstraints which will 
    call a function to get the constraint list upon request.

    """
    def __init__(self, func, *args, **kwds):
        """ Initialize a DeferredConstraintsFunction.

        Parameters
        ----------
        func : callable
            A callable object which will return the list of constraints.
        
        *args
            The arguments to pass to 'func'.
        
        **kwds
            The keyword arguments to pass to 'func'.
        
        """
        super(DeferredConstraintsFunction, self).__init__(func, *args, **kwds)
        self.func = func
        self.args = args
        self.kwds = kwds

    def _get_constraints(self, component):
        """ Abstract method implementation which calls the underlying 
        function to generate the list of constraints.

        """
        return self.func(*self.args, **self.kwds)
    

class AbutmentHelper(DeferredConstraints):
    """ A concrete implementation of DeferredConstraints which will
    lay out its components by abutting them in a given orientation.

    """
    def __init__(self, *items, **metadata):
        """ Initialize an AbutmentHelper.

        Parameters
        ----------
        *items
            The components to abut in the given orientation.

        **metadata
            Metadata related to how the abutment should behave. The
            following options are currently supported:
                
                orientation
                    A string which is either 'horizontal' or 'vertical'
                    which indicates the abutment orientation. The 
                    default is 'vertical'.
                
                spacing
                    An integer >= 0 which indicates how many pixels of
                    inter-element spacing to use during abutment. The 
                    default is the value of DefaultSpacing.ABUTMENT.

        """
        super(AbutmentHelper, self).__init__(*items, **metadata)
        self.items = items
        self.orientation = metadata.get('orientation', 'vertical')
        self.spacing = metadata.get('spacing', DefaultSpacing.ABUTMENT)

    def __repr__(self):
        items = ', '.join(map(repr, self.items))
        return '{0}({1})'.format(self.orientation, items)

    def _get_constraints(self, component):
        """ Abstract method implementation which applies the constraints
        to the given items, after filtering them for None values.

        """
        items = [item for item in self.items if item is not None]
        if self.clear_invisible:
            items = clear_invisible(items)
        cns = []
        factories = AbutmentConstraintFactory.from_items(
            items, self.orientation, self.spacing,
        )
        for f in factories:
            cns.extend(f.constraints())
        return cns


class AlignmentHelper(DeferredConstraints):
    """ A deferred constraints helper class that lays out with a given
    anchor to align.

    """
    def __init__(self, *items, **metadata):
        """ Initialize an AlignmentHelper.

        Parameters
        ----------
        *items
            The components to align on the given anchor.

        **metadata
            Metadata related to how the abutment should behave. The
            following options are currently supported:
                
                anchor
                    A string which is either 'left', 'right', 'top', 
                    'bottom', 'v_center', or 'h_center'. The default
                    is 'v_center'.
                
                spacing
                    An integer >= 0 which indicates how many pixels of
                    inter-element spacing to use during alignement. The 
                    default is the value of DefaultSpacing.ALIGNMENT.

        """
        super(AlignmentHelper, self).__init__(*items, **metadata)
        self.items = items
        self.anchor = metadata.get('anchor', 'v_center')
        self.spacing = metadata.get('spacing', DefaultSpacing.ALIGNMENT)

    def __repr__(self):
        items = ', '.join(map(repr, self.items))
        return 'align({0!r}, {1})'.format(self.anchor, items)

    def _get_constraints(self, component):
        """ Abstract method implementation which applies the constraints
        to the given items, after filtering them for None values.

        """
        items = [item for item in self.items if item is not None]
        if self.clear_invisible:
            items = clear_invisible(items)
        cns = []
        factories = AlignmentConstraintFactory.from_items(
            items, self.anchor, self.spacing,
        )
        for f in factories:
            cns.extend(f.constraints())
        return cns

    
class LinearBoxHelper(DeferredConstraints):
    """ A DeferredConstraints helper class that lays out Components 
    either horizontally or vertically and taking up all of the space 
    in the orthogonal direction. Instances of this class are nestable.

    """
    #: A mapping orientation to the anchor names needed to make the
    #: constraints on the containing component.
    orientation_map = {
        'horizontal': ('left', 'right'),
        'vertical': ('top', 'bottom'),
    }

    def __init__(self, *items, **metadata):
        """ Initialize an AlignmentHelper.

        Parameters
        ----------
        *items
            The components to align on the given anchor.

        **metadata
            Metadata related to how the abutment should behave. The
            following options are currently supported:
                
                orientation
                    A string which is either 'horizontal' or 'vertical'
                    which indicates the abutment orientation. The 
                    default is 'vertical'.
                
                spacing
                    An integer >= 0 which indicates how many pixels of
                    inter-element spacing to use during abutment. The 
                    default is the value of DefaultSpacing.ABUTMENT.
                
                margin
                    A int, tuple of ints, or Box of ints >= 0 which 
                    indicate how many pixels of margin to add around 
                    the bounds of the box. The default is the value of 
                    DefaultSpacing.BOX_MARGIN.
                
        """
        super(LinearBoxHelper, self).__init__(*items, **metadata)

        orientation = metadata.get('orientation', 'vertical')
        if orientation == 'horizontal':
            ortho_orientation = 'vertical'
        elif orientation == 'vertical':
            ortho_orientation = 'horizontal'
        else:
            msg = ("Expected 'horizontal' or 'vertical' for orientation. "
                   "Got {!r} instead.")
            raise ValueError(msg.format(orientation))
        
        self.items = items
        self.orientation = orientation
        self.ortho_orientation = ortho_orientation
        self.spacing = metadata.get('spacing', DefaultSpacing.ABUTMENT)
        self.margins = Box(metadata.get('margins', DefaultSpacing.BOX_MARGINS))
        
        for attr in ('top', 'bottom', 'left', 'right'):
            label = '{0}_{1:x}'.format(self.orientation[0]+'box', id(self))
            var = ConstraintVariable('{0}_{1}'.format(attr, label))
            setattr(self, attr, var)
    
    def __repr__(self):
        items = ', '.join(map(repr, self.items))
        return '{0}box({1})'.format(self.orientation[0], items)

    def _get_constraints(self, component):
        """ Abstract method implementation which applies the constraints
        to the given items, after filtering them for None values.

        """
        items = [item for item in self.items if item is not None]
        if self.clear_invisible:
            items = clear_invisible(items)

        if len(items) == 0:
            return []
        
        get = getattr
        first_name, last_name = self.orientation_map[self.orientation]
        first_boundary = get(self, first_name)
        last_boundary = get(self, last_name)
        first_name, last_name = self.orientation_map[self.ortho_orientation]
        first_ortho_boundary = get(self, first_name)
        last_ortho_boundary = get(self, last_name)

        # Setup the initial outer constraints of the box
        if component is not None:
            # This box helper is inside a real component, not just nested 
            # inside of another box helper. Check if the component is a
            # PaddingConstraints object and use it's contents anchors.
            attrs = ['top', 'bottom', 'left', 'right']
            if isinstance(component, PaddingConstraints):
                other_attrs = ['contents_' + attr for attr in attrs]
            else:
                other_attrs = attrs[:]
            constraints = [
                get(self, attr) == get(component, other) 
                for (attr, other) in zip(attrs, other_attrs)
            ]
        else:
            constraints = []
        
        # Create the margin spacers that will be used.
        margins = self.margins
        if self.orientation == 'vertical':
            first_spacer = EqSpacer(margins.top)
            last_spacer = EqSpacer(margins.bottom)
            first_ortho_spacer = FlexSpacer(margins.left)
            last_ortho_spacer = FlexSpacer(margins.right)
        else:
            first_spacer = EqSpacer(margins.left)
            last_spacer = EqSpacer(margins.right)
            first_ortho_spacer = FlexSpacer(margins.top)
            last_ortho_spacer = FlexSpacer(margins.bottom)

        # Add a pre and post padding spacer if the user hasn't specified 
        # their own spacer as the first/last element of the box items.
        if not is_spacer(items[0]):
            pre_along_args = [first_boundary, first_spacer]
        else:
            pre_along_args = [first_boundary]
        if not is_spacer(items[-1]):
            post_along_args = [last_spacer, last_boundary]
        else:
            post_along_args = [last_boundary]

        # Accummulate the constraints in the direction of the layout
        along_args = pre_along_args + items + post_along_args
        kwds = dict(
            orientation=self.orientation, spacing=self.spacing,
            clear_invisible=self.clear_invisible,
        )
        helpers = [AbutmentHelper(*along_args, **kwds)]
        kwds['orientation'] = self.ortho_orientation
        for item in items:
            # Add the helpers for the ortho constraints
            if isinstance(item, ABConstrainable):
                items = (
                    first_ortho_boundary, first_ortho_spacer,
                    item, last_ortho_spacer, last_ortho_boundary,
                )
                helpers.append(AbutmentHelper(*items, **kwds)) 
            # Pull out nested helpers so that their constraints get
            # generated during the pass over the helpers list.
            if isinstance(item, DeferredConstraints):
                helpers.append(item)
        
        # Pass over the list of child helpers and generate the 
        # flattened list of constraints.
        for helper in helpers:
            constraints.extend(helper.get_constraints(None))

        return constraints


ABConstrainable.register(LinearBoxHelper)


#------------------------------------------------------------------------------
# Abstract Constraint Factory
#------------------------------------------------------------------------------
class AbstractConstraintFactory(object):
    """ An abstract constraint factory class. Subclasses must implement
    the 'constraints' method implement which returns a LinearConstraint
    instance.

    """
    __metaclass__ = ABCMeta

    @staticmethod
    def validate(items):
        """ A validator staticmethod that insures a sequence of items is 
        appropriate for generating a sequence of linear constraints. The 
        following conditions are verified of the sequence of given items:

            * The number of items in the sequence is 0 or >= 2.

            * The first and last items are instances of either
              LinearSymbolic or Constrainable.

            * All of the items in the sequence are instances of 
              LinearSymbolic, Constrainable, Spacer, or int.
    
        If any of the above conditions do not hold, an exception is 
        raised with a (hopefully) useful error message.

        """
        if len(items) == 0:
            return

        if len(items) < 2:
            msg = 'Two or more items required to setup abutment constraints.'
            raise ValueError(msg)
        
        extrema_types = (LinearSymbolic, ABConstrainable)
        def extrema_test(item):
            return isinstance(item, extrema_types)
        
        item_types = (LinearSymbolic, ABConstrainable, Spacer, int)
        def item_test(item):
            return isinstance(item, item_types)

        if not all(extrema_test(item) for item in (items[0], items[-1])):
            msg = ('The first and last items of a constraint sequence '
                   'must be anchors or Components. Got %s instead.')
            args = [type(items[0]), type(items[1])]
            raise TypeError(msg % args)
        
        if not all(map(item_test, items)):
            msg = ('The allowed items for a constraint sequence are'
                   'anchors, Components, Spacers, and ints. '
                   'Got %s instead.')
            args = [type(item) for item in items]
            raise TypeError(msg % args)

    @abstractmethod
    def constraints(self):
        """ An abstract method which must be implemented by subclasses.
        It should return a list of LinearConstraint instances.

        """
        raise NotImplementedError


#------------------------------------------------------------------------------
# Abstract Constraint Factory Implementations
#------------------------------------------------------------------------------
class BaseConstraintFactory(AbstractConstraintFactory):
    """ A base constraint factory class that implements basic common
    logic. It is not meant to be used directly but should rather be 
    subclassed to be useful.

    """
    def __init__(self, first_anchor, spacer, second_anchor):
        """ Create an base constraint instance.

        Parameters
        ----------
        first_anchor : LinearSymbolic
            A symbolic object that can be used in a constraint expression.
        
        spacer : Spacer
            A spacer instance to put space between the items.
        
        second_anchor : LinearSymbolic
            The second anchor for the constraint expression.

        """
        self.first_anchor = first_anchor
        self.spacer = spacer
        self.second_anchor = second_anchor

    def constraints(self):
        """ Returns LinearConstraint instance which is formed through
        an appropriate linear expression for the given space between 
        the anchors.

        """
        first = self.first_anchor
        second = self.second_anchor
        spacer = self.spacer
        return spacer.constrain(first, second)


class SequenceConstraintFactory(BaseConstraintFactory):
    """ A BaseConstraintFactory subclass that represents a constraint
    between two anchors of different components separated by some amount
    of space. It has a '_make_cns' classmethod which will create a list
    of constraint factory instances from a sequence of items, the two
    anchor names, and a default spacing.

    """
    @classmethod
    def _make_cns(cls, items, first_anchor_name, second_anchor_name, spacing):
        """ A classmethod that generates a list of constraints factories
        given a sequence of items, two anchor names, and default spacing. 

        Parameters
        ----------
        items : sequence
            A valid sequence of constrainable objects. These inclue
            instances of Constrainable, LinearSymbolic, Spacer,
            and int.
        
        first_anchor_name : string
            The name of the anchor on the first item in a constraint
            pair.
        
        second_anchor_name : string
            The name of the anchor on the second item in a constraint
            pair.
        
        spacing : int
            The spacing to use between items if no spacing is explicitly 
            provided by in the sequence of items.
        
        Returns
        -------
        result : list
            A list of constraint factory instance.
        
        """
        # Make sure the items we'll be dealing with are valid for the
        # algorithm. This is a basic validation. Further error handling
        # is performed as needed.
        cls.validate(items)
    
        # The list of constraints we'll be creating for the given 
        # sequence of items.
        cns = []

        # The list of items is treated as a stack. So we want to first
        # reverse it so the first items are at the top of the stack.
        items = list(reversed(items))

        while items:

            # Grab the item that will provide the first anchor
            first_item = items.pop()

            # first_item will be a Constrainable or a LinearSymbolic.
            # For the first iteration, this is enforced by 'validate'.
            # For subsequent iterations, this condition is enforced by 
            # the fact that this loop only pushes those types back onto 
            # the stack.
            if isinstance(first_item, ABConstrainable):
                first_anchor = getattr(first_item, first_anchor_name)
            elif isinstance(first_item, LinearSymbolic):
                first_anchor = first_item
            else:
                raise TypeError('This should never happen')
            
            # Grab the next item off the stack. It will be an instance
            # of Constrainable, LinearSymbolic, Spacer, or int. If it
            # can't provide an anchor, we grab the item after it which
            # *should* be able to provide one. If no space is given, we 
            # use the provided default space.
            next_item = items.pop()
            if isinstance(next_item, Spacer):
                spacer = next_item
                second_item = items.pop()
            elif isinstance(next_item, int):
                spacer = EqSpacer(next_item)
                second_item = items.pop()
            elif isinstance(next_item, (ABConstrainable, LinearSymbolic)):
                spacer = EqSpacer(spacing)
                second_item = next_item
            else:
                raise ValueError('This should never happen')
            
            # If the second_item can't provide an anchor, such as two 
            # spacers next to each other, then this is an error and we
            # raise an appropriate exception.
            if isinstance(second_item, ABConstrainable):
                second_anchor = getattr(second_item, second_anchor_name)   
            elif isinstance(second_item, LinearSymbolic):
                second_anchor = second_item
            else:
                msg = 'Expected anchor or Constrainable. Got %r instead.'
                raise TypeError(msg % second_item)
            
            # Create the class instance for this constraint
            factory = cls(first_anchor, spacer, second_anchor)

            # If there are still items on the stack, then the second_item
            # will be used as the first_item in the next iteration. 
            # Otherwise, we have exhausted all constraints and can exit.
            if items:
                items.append(second_item)

            # Finally, store away the created factory for returning.
            cns.append(factory)

        return cns


class AbutmentConstraintFactory(SequenceConstraintFactory):
    """ A SequenceConstraintFactory subclass that represents an abutment 
    constraint, which is a constraint between two anchors of different 
    components separated by some amount of space. It has a 'from_items'
    classmethod which will create a sequence of abutment constraints
    from a sequence of items, a direction, and default spacing.

    """
    #: A mapping from orientation to the order of anchor names to 
    #: lookup for a pair of items in order to make the constraint.
    orientation_map = {
        'horizontal': ('right', 'left'),
        'vertical': ('bottom', 'top'),
    }

    @classmethod
    def from_items(cls, items, orientation, spacing):
        """ A classmethod that generates a list of abutment constraints
        given a sequence of items, an orientation, and default spacing. 

        Parameters
        ----------
        items : sequence
            A valid sequence of constrainable objects. These inclue
            instances of Constrainable, LinearSymbolic, Spacer,
            and int.
        
        orientation : string
            Either 'vertical' or 'horizontal', which represents the 
            orientation in which to abut the items.
        
        spacing : int
            The spacing to use between items if no spacing is explicitly 
            provided by in the sequence of items.
        
        Returns
        -------
        result : list
            A list of AbutmentConstraint instances.
        
        Notes
        ------ 
        The order of abutment is left-to-right for horizontal direction 
        and top-to-bottom for vertical direction.

        """
        # Grab the tuple of anchor names to lookup for each pair of 
        # items in order to make the connection.
        orient = cls.orientation_map.get(orientation)
        if orient is None:
            msg = ("Valid orientations for abutment are 'vertical' or "
                   "'horizontal'. Got %r instead.")
            raise ValueError(msg % orientation)
        first_name, second_name = orient
        return cls._make_cns(items, first_name, second_name, spacing)


class AlignmentConstraintFactory(SequenceConstraintFactory):
    """ A SequenceConstraintFactory subclass which represents an 
    alignmnent constraint, which is a constraint between two anchors of
    different components which are aligned but may be separated by some
    amount of space. It provides a 'from_items' classmethod which will 
    create a  list of alignment constraints from a sequence of items an 
    anchor name, and a default spacing.

    """
    @classmethod
    def from_items(cls, items, anchor_name, spacing):
        """ A classmethod that will create a seqence of alignment
        constraints given a sequence of items, an anchor name, and
        a default spacing.
        
        Parameters
        ----------
        items : sequence
            A valid sequence of constrainable objects. These inclue
            instances of Constrainable, LinearSymbolic, Spacer,
            and int.
        
        anchor_name : string
            The name of the anchor on the components which should be
            aligned. Either 'left', 'right', 'top', 'bottom', 'v_center',
            or 'h_center'.
        
        spacing : int
            The spacing to use between items if no spacing is explicitly 
            provided by in the sequence of items.
        
        Returns
        -------
        result : list
            A list of AbutmentConstraint instances.

        Notes
        -----
        For every item in the sequence, if the item is a component, then
        anchor for the given anchor_name on that component will be used. 
        If a LinearSymbolic is given, then that symbolic will be used and
        the anchor_name will be ignored. Specifying space between items 
        via integers or spacers is allowed.

        """
        return cls._make_cns(items, anchor_name, anchor_name, spacing)


#------------------------------------------------------------------------------
# Spacers
#------------------------------------------------------------------------------
class Spacer(object):
    """ An abstract base class for spacers. Subclasses must implement 
    the 'constrain' method.

    """
    __metaclass__ = ABCMeta

    def __init__(self, amt, strength=None, weight=None):
        self.amt = max(0, amt)
        self.strength = strength
        self.weight = weight

    def when(self, switch):
        """ A simple method that can be used to switch off the generated
        space depending on a boolean value.

        """
        if switch:
            return self
    
    def constrain(self, first_anchor, second_anchor):
        """ Returns the list of generated constraints appropriately
        weighted by the default strength and weight, if provided.

        """
        constraints = self._constrain(first_anchor, second_anchor)
        strength = self.strength
        if strength is not None:
            constraints = [cn | strength for cn in constraints]
        weight = self.weight
        if weight is not None:
            constraints = [cn | weight for cn in constraints]
        return constraints

    @abstractmethod
    def _constrain(self, first_anchor, second_anchor):
        """ An abstract method. Subclasses should implement this method 
        to return a list of LinearConstraint instances which separate
        the two anchors according to the amount of space represented
        by the spacer.

        """
        raise NotImplementedError


class EqSpacer(Spacer):
    """ A spacer which represents a fixed amount of space.

    """
    def _constrain(self, first_anchor, second_anchor):
        """ A constraint of the form (anchor_1 + space == anchor_2)

        """
        return [(first_anchor + self.amt) == second_anchor]


class LeSpacer(Spacer):
    """ A spacer which represents a flexible space with a maximum value.

    """
    def _constrain(self, first_anchor, second_anchor):
        """ A constraint of the form (anchor_1 + space >= anchor_2)
        That is, the visible space must be less than or equal to the
        given amount. An additional constraint is applied which 
        constrains (anchor_1 <= anchor_2) to prevent negative space.

        """
        return [(first_anchor + self.amt) >= second_anchor,
                first_anchor <= second_anchor]


class GeSpacer(Spacer):
    """ A spacer which represents a flexible space with a minimum value.

    """
    def _constrain(self, first_anchor, second_anchor):
        """ A constraint of the form (anchor_1 + space <= anchor_2)
        That is, the visible space must be greater than or equal to
        the given amount.

        """
        return [(first_anchor + self.amt) <= second_anchor]


class FlexSpacer(Spacer):
    """ A spacer which represents a space with a hard minimum, but also 
    a weaker preference for being that minimum.

    """
    def __init__(self, amt, min_strength='required', min_weight=1.0, eq_strength='medium', eq_weight=1.25):
        self.amt = max(0, amt)
        self.min_strength = min_strength
        self.min_weight = min_weight
        self.eq_strength = eq_strength
        self.eq_weight = eq_weight

    def constrain(self, first_anchor, second_anchor):
        """ Return list of LinearConstraint objects that are appropriate to
        separate the two anchors according to the amount of space represented by
        the spacer.

        """
        return self._constrain(first_anchor, second_anchor)

    def _constrain(self, first_anchor, second_anchor):
        """ Constraints of the form (anchor_1 + space <= anchor_2) and
        (anchor_1 + space == anchor_2)

        """
        return [
            ((first_anchor + self.amt) <= second_anchor) | self.min_strength | self.min_weight,
            ((first_anchor + self.amt) == second_anchor) | self.eq_strength | self.eq_weight,
        ]


class LayoutSpacer(Spacer):
    """ A Spacer instance which supplies convenience symbolic and normal
    methods to facilitate specifying spacers in layouts.

    """
    def __call__(self, *args, **kwargs):
        return self.__class__(*args, **kwargs)
    
    def __eq__(self, other):
        if not isinstance(other, int):
            raise TypeError('space can only be created from ints')
        return EqSpacer(other, self.strength, self.weight)
    
    def __le__(self, other):
        if not isinstance(other, int):
            raise TypeError('space can only be created from ints')
        return LeSpacer(other, self.strength, self.weight)
    
    def __ge__(self, other):
        if not isinstance(other, int):
            raise TypeError('space can only be created from ints')
        return GeSpacer(other, self.strength, self.weight)
    
    def _constrain(self, first_anchor, second_anchor):
        """ Returns a greater than or equal to spacing constraint.

        """
        spacer = GeSpacer(self.amt, self.strength, self.weight)
        return spacer._constrain(first_anchor, second_anchor)
        
    def flex(self, **kwargs):
        """ Returns a flex spacer for the current amount.

        """
        return FlexSpacer(self.amt, **kwargs)


#------------------------------------------------------------------------------
# Layout factory functions
#------------------------------------------------------------------------------
def horizontal(*items, **metadata):
    """ Create a DeferredConstraints object composed of horizontal 
    abutments for the given sequence of items.

    """
    metadata['orientation'] = 'horizontal'
    return AbutmentHelper(*items, **metadata)


def vertical(*items, **metadata):
    """ Create a DeferredConstraints object composed of vertical 
    abutments for the given sequence of items.

    """
    metadata['orientation'] = 'vertical'
    return AbutmentHelper(*items, **metadata)


def hbox(*items, **metadata):
    """ Create a DeferredConstraints object composed of horizontal 
    abutments for a given sequence of items.

    """
    metadata['orientation'] = 'horizontal'
    return LinearBoxHelper(*items, **metadata)


def vbox(*items, **metadata):
    """ Create a DeferredConstraints object composed of vertical abutments 
    for a given sequence of items.

    """
    metadata['orientation'] = 'vertical'
    return LinearBoxHelper(*items, **metadata)


def align(anchor, *items, **metadata):
    """ Align the given anchors of the given components. Inter-component 
    spacing is allowed.

    """
    metadata.setdefault('anchor', anchor)
    return AlignmentHelper(*items, **metadata)


@deprecated
def align_left(*items, **metadata):
    """ Align the left anchors of the given components. Inter-component
    spacing is allowed.

    """
    return align('left', *items, **metadata)


@deprecated
def align_right(*items, **metadata):
    """ Align the right anchors of the given components. Inter-component
    spacing is allowed.
    
    """
    return align('right', *items, **metadata)


@deprecated
def align_top(*items, **metadata):
    """ Align the top anchors of the given components. Inter-component
    spacing is allowed.
    
    """
    return align('top', *items, **metadata)


@deprecated
def align_bottom(*items, **metadata):
    """ Align the bottom anchors of the given components. Inter-component
    spacing is allowed.
    
    """
    return align('bottom', *items, **metadata)


@deprecated
def align_v_center(*items, **metadata):
    """ Align the v_center anchors of the given components. Inter-component
    spacing is allowed.
    
    """
    return align('v_center', *items, **metadata)


@deprecated
def align_h_center(*items, **metadata):
    """ Align the h_center anchors of the given components. Inter-component
    spacing is allowed.
    
    """
    return align('h_center', *items, **metadata)


#------------------------------------------------------------------------------
# Toolkit items
#------------------------------------------------------------------------------
LAYOUT_HELPERS = {
    'horizontal': horizontal,
    'vertical': vertical,
    'hbox': hbox,
    'vbox': vbox,
    'align_left': align_left,
    'align_right': align_right,
    'align_top': align_top,
    'align_bottom': align_bottom,
    'align_v_center': align_v_center,
    'align_h_center': align_h_center,
    'align': align,
    '_space_': LayoutSpacer(DefaultSpacing.ABUTMENT), # Backwards compatibility
    'spacer': LayoutSpacer(DefaultSpacing.ABUTMENT),
}

