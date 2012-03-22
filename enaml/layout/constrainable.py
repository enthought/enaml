#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import (
    HasStrictTraits, List, Property, Instance, Bool, on_trait_change,
    Tuple, Either
)

from .box_model import BoxModel, PaddingBoxModel
from .geometry import Box

from ..core.trait_types import CoercingInstance
from ..enums import PolicyEnum


def _get_from_box_model(self, name):
    """ Property getter for all attributes that come from the box model.

    """
    return getattr(self._box_model, name)


class Constrainable(HasStrictTraits):
    """ A mixin class which adds the facilities necessary for a component
    to be managed by a constraints-based layout manager. This mixin is
    expecting to have BaseComponent in the mro.

    """
    #: The list of user-specified constraints or constraint-generating
    #: objects for this component.
    constraints = List
    
    #: Whether or not the component is visible. An invisible component
    #: will be ignored by constraints layout helpers.
    visible = Bool(True)

    #: A read-only symbolic object that represents the left boundary of 
    #: the component
    left = Property(fget=_get_from_box_model)

    #: A read-only symbolic object that represents the top boundary of 
    #: the component
    top = Property(fget=_get_from_box_model)

    #: A read-only symbolic object that represents the width of the 
    #: component
    width = Property(fget=_get_from_box_model)

    #: A read-only symbolic object that represents the height of the 
    #: component
    height = Property(fget=_get_from_box_model)

    #: A read-only symbolic object that represents the right boundary 
    #: of the component
    right = Property(fget=_get_from_box_model)

    #: A read-only symbolic object that represents the bottom boundary 
    #: of the component
    bottom = Property(fget=_get_from_box_model)

    #: A read-only symbolic object that represents the vertical center 
    #: of the component
    v_center = Property(fget=_get_from_box_model)

    #: A read-only symbolic object that represents the horizontal 
    #: center of the component
    h_center = Property(fget=_get_from_box_model)

    #: The private storage the box model instance for this component.
    _box_model = Instance(BoxModel)
    def __box_model_default(self):
        return BoxModel(self)

    #--------------------------------------------------------------------------
    # Change Handlers
    #--------------------------------------------------------------------------
    @on_trait_change('constraints, constraints_items')
    def _on_constrainable_deps_changed(self):
        """ A change handler which requests a relayout when the constraints
        change, provided that the component is initialized.

        """
        if self.initialized:
            self.request_relayout()
    
    #--------------------------------------------------------------------------
    # Geometry Methods
    #--------------------------------------------------------------------------
    def update_layout_geometry(self, dx, dy):
        """ An abstract method which must be implemented by subclasses.
        This method is called during a layout pass when the symbolic
        constraint variables of the component are filled with their
        solved values. The component should use the opportunity to
        update its layout geometry with the updated information.

        Parameters
        ----------
        dx : int
            The x-direction offset of the parent of this component from
            the root component on which the solved dimensions are based.
        
        dy : int
            The y-direction offset of the parent of this component from
            the root component on which the solved dimensions are based.
        
        Returns
        -------
        result : (x, y)
            The solved (x, y) position of this component relative to
            the root component on which the solved dimensions are bsaed.

        """
        raise NotImplementedError
    
    #--------------------------------------------------------------------------
    # Constraint Handling
    #--------------------------------------------------------------------------
    def hard_constraints(self):
        """ Returns the list of required symbolic constraints for the 
        component. These are constraints that apply to both the internal
        layout computations of a component as well as any calculations
        of containers which may parent this component. The default 
        implementation constrains the variables 'left', 'right', 
        'width', and 'height' to >= 0 required.

        """
        cns = [
            self.left >= 0, self.top >= 0, 
            self.width >= 0, self.height >= 0,
        ]
        return cns

    def size_hint_constraints(self):
        """ Returns the list of constraints which are related to the
        preferred size of the component. These constraints should be
        made independent of the 'hard_constraints' and are only of
        use in the calculations of potential parent containers. The 
        default implementation of this method returns an empty list.

        """
        return []
            
    def component_constraints(self):
        """ A set of constraints that should always be applied to this 
        type of component. The constraints generated by this method
        are use in the internal layout calculations of a component. 
        The default implementation returns an empty list.

        """
        return []

    def user_constraints(self):
        """ Returns the list of constraints specified by the user or the
        list of constraints computed by 'default_user_constraints' if the
        user has not supplied their own list. The list is used for 
        internal layout calculations.

        """
        cns = self.constraints
        if not cns:
            cns = self.default_user_constraints()
        return cns

    def default_user_constraints(self):
        """ Constraints to use if the constraints trait is an empty list.
        This default implementation returns an empty list.

        """
        return []


class PaddingConstraints(Constrainable):
    """ A Constrainable subclass which adds padding to the box model.

    """
    #: A read-only symbolic object that represents the internal left 
    #: padding of the container.
    padding_left = Property(fget=_get_from_box_model)

    #: A read-only symbolic object that represents the internal right 
    #: padding of the container.
    padding_right = Property(fget=_get_from_box_model)

    #: A read-only symbolic object that represents the internal top 
    #: padding of the container.
    padding_top = Property(fget=_get_from_box_model)

    #: A read-only symbolic object that represents the internal bottom 
    #: padding of the container.
    padding_bottom = Property(fget=_get_from_box_model)

    #: A read-only symbolic object that represents the internal left 
    #: boundary of the content area of the container.
    contents_left = Property(fget=_get_from_box_model)

    #: A read-only symbolic object that represents the internal right 
    #: boundary of the content area of the container.
    contents_right = Property(fget=_get_from_box_model)

    #: A read-only symbolic object that represents the internal top 
    #: boundary of the content area of the container.
    contents_top = Property(fget=_get_from_box_model)

    #: A read-only symbolic object that represents the internal bottom 
    #: boundary of the content area of the container.
    contents_bottom = Property(fget=_get_from_box_model)

    #: A read-only symbolic object that represents the internal width of
    #: the content area of the container.
    contents_width = Property(fget=_get_from_box_model)

    #: A read-only symbolic object that represents the internal height of
    #: the content area of the container.
    contents_height = Property(fget=_get_from_box_model)

    #: A read-only symbolic object that represents the internal center 
    #: along the vertical direction the content area of the container.
    contents_v_center = Property(fget=_get_from_box_model)

    #: A read-only symbolic object that represents the internal center 
    #: along the horizontal direction of the content area of the container.
    contents_h_center = Property(fget=_get_from_box_model)

    #: A box object which holds the padding for this component. The 
    #: default padding is Box(0, 0, 0, 0).
    padding = CoercingInstance(Box, default=Box(0, 0, 0, 0))

    #: The PolicyEnum for the strength with which to enforce the padding.
    #: This can be a single policy value to apply to everything, or a 
    #: 4-tuple of policies to apply to the individual padding.           
    padding_strength = Either(
        PolicyEnum, Tuple(PolicyEnum, PolicyEnum, PolicyEnum, PolicyEnum),
        default = 'required'
    )

    #: The private storage the box model instance for this component. 
    _box_model = Instance(PaddingBoxModel, ())
    def __box_model_default(self):
        return PaddingBoxModel(self)
    
    #--------------------------------------------------------------------------
    # Change Handlers
    #--------------------------------------------------------------------------
    @on_trait_change('padding', 'padding_strength')
    def _on_padding_deps_changed(self):
        """ A change handler which requests a relayout if the padding or
        padding strengths change, provided that the component is fully
        initialized.

        """
        if self.initialized:
            self.request_relayout()
    
    #--------------------------------------------------------------------------
    # Constraint Handling
    #--------------------------------------------------------------------------
    def padding_constraints(self):
        """ Returns the list of symbolic constraints for the padding of 
        the component. These constraints apply to the internal layout 
        calculations of an object. The default implementation constrains 
        the padding according the values in the 'padding' attribute and
        the strengths in 'padding_strength' attribute. It also places a 
        required constraint >= 0 on every padding element.

        """
        cns = []
        padding = self.padding
        tags = ('top', 'right', 'bottom', 'left')
        strengths = self.padding_strength
        if isinstance(strengths, basestring):
            strengths = (strengths,) * 4
        for tag, strength, padding in zip(tags, strengths, padding):
            tag = 'padding_' + tag
            sym = getattr(self, tag)
            cns.append(sym >= 0)
            if strength != 'ignore':
                cns.append((sym == padding) | strength)
        return cns

