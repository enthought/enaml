#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Property, Enum, Instance, List

from enaml.application import Application, ScheduledTask
from enaml.layout.ab_constrainable import ABConstrainable
from enaml.layout.box_model import BoxModel
from enaml.layout.layout_helpers import expand_constraints

from .widget import Widget


#: A traits enum which defines the allowable constraints strengths.
PolicyEnum = Enum('ignore', 'weak', 'medium', 'strong', 'required')


def get_from_box_model(self, name):
    """ Property getter for all attributes that come from the box model.

    """
    return getattr(self._box_model, name)


class ConstraintsWidget(Widget):
    """ A Widget subclass which adds constraint information.

    A ConstraintsWidget is augmented with symbolic constraint variables
    which define a box model on the widget. This box model is used to
    declare constraints between this widget and other components which
    participate in constraints-based layout.

    Constraints are added to a widget by assigning a list to the
    'constraints' attribute. This list may contain raw LinearConstraint
    objects (which are created by manipulating the symbolic constraint
    variables) or DeferredConstraints objects which generated these
    LinearConstraint objects on-the-fly.

    A ConstraintsWidget also has a 'constraints_id' which is a uuid
    given to the object and to each of its constraint variables in
    order to track ownership of the constraint variables. This id
    is automatically generated, and should not be modified by the
    user.

    """
    #: The list of user-specified constraints or constraint-generating
    #: objects for this component.
    constraints = List

    #: A read-only symbolic object that represents the left boundary of
    #: the component
    left = Property(fget=get_from_box_model)

    #: A read-only symbolic object that represents the top boundary of
    #: the component
    top = Property(fget=get_from_box_model)

    #: A read-only symbolic object that represents the width of the
    #: component
    width = Property(fget=get_from_box_model)

    #: A read-only symbolic object that represents the height of the
    #: component
    height = Property(fget=get_from_box_model)

    #: A read-only symbolic object that represents the right boundary
    #: of the component
    right = Property(fget=get_from_box_model)

    #: A read-only symbolic object that represents the bottom boundary
    #: of the component
    bottom = Property(fget=get_from_box_model)

    #: A read-only symbolic object that represents the vertical center
    #: of the component
    v_center = Property(fget=get_from_box_model)

    #: A read-only symbolic object that represents the horizontal
    #: center of the component
    h_center = Property(fget=get_from_box_model)

    #: How strongly a component hugs it's width hint. Valid strengths
    #: are 'weak', 'medium', 'strong', 'required' and 'ignore'. Default
    #: is 'strong'. This trait should be overridden on a per-control
    #: basis to specify a logical default for the given control.
    hug_width = PolicyEnum('strong')

    #: How strongly a component hugs it's height hint. Valid strengths
    #: are 'weak', 'medium', 'strong', 'required' and 'ignore'. Default
    #: is 'strong'. This trait should be overridden on a per-control
    #: basis to specify a logical default for the given control.
    hug_height = PolicyEnum('strong')

    #: How strongly a component resists clipping its contents. Valid
    #: strengths are 'weak', 'medium', 'strong', 'required' and 'ignore'.
    #: The default is 'strong' for width.
    resist_width = PolicyEnum('strong')

    #: How strongly a component resists clipping its contents. Valid
    #: strengths are 'weak', 'medium', 'strong', 'required' and 'ignore'.
    #: The default is 'strong' for height.
    resist_height = PolicyEnum('strong')

    #: The private application task used to collapse layout messages.
    _layout_task = Instance(ScheduledTask)

    #: The private storage the box model instance for this component.
    _box_model = Instance(BoxModel)
    def __box_model_default(self):
        return BoxModel(self.object_id)

    #--------------------------------------------------------------------------
    # Initialization
    #--------------------------------------------------------------------------
    def snapshot(self):
        """ Populates the initial attributes dict for the component.

        A ConstraintsWidget adds the 'layout' key to the creation
        attributes dict. The value is a dict with the following keys.

        'constraints'
            A list of dictionaries representing linear constraints.

        'resist_clip'
            A tuple containing width and height clip policies.

        'hug'
            A tuple containing width and height hug policies.

        """
        snap = super(ConstraintsWidget, self).snapshot()
        snap['layout'] = self._layout_info()
        return snap

    def bind(self):
        """ Binds the change handlers for the component.

        """
        super(ConstraintsWidget, self).bind()
        d = 'constraints, hug_width, hug_height, resist_width, resist_height'
        self.on_trait_change(self._send_relayout, d)

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def when(self, switch):
        """ A method which returns `self` or None based on the truthness
        of the argument.

        This can be useful to easily turn off the effects of an object
        in constraints-based layout.

        Parameters
        ----------
        switch : bool
            A boolean which indicates whether this instance or None
            should be returned.

        Returns
        -------
        result : self or None
            If 'switch' is boolean True, self is returned. Otherwise,
            None is returned.

        """
        if switch:
            return self

    #--------------------------------------------------------------------------
    # Message Handling
    #--------------------------------------------------------------------------
    def _send_relayout(self):
        """ Send the 'relayout' action to the client widget.

        If an Enaml Application instance exists, then multiple `relayout`
        actions will be collapsed into a single action that will be sent
        on the next cycle of the event loop. If no application exists,
        then the action is sent immediately.

        """
        # The relayout action is deferred until the next cycle of the
        # event loop for two reasons: 1) So that multiple relayout
        # requests can be collapsed into a single action. 2) So that
        # all child events (which are fired synchronously) can finish
        # processing and send their actions to the client before the
        # relayout request is sent. The action itself is batched so
        # that it can be sent along with any object tree changes.
        app = Application.instance()
        if app is not None:
            task = self._layout_task
            if task is None:
                def notifier(ignored):
                    self._layout_task = None
                def layout_task():
                    self.batch_action('relayout', self._layout_info())
                task = app.schedule(layout_task)
                task.notify(notifier)
                self._layout_task = task

    #--------------------------------------------------------------------------
    # Constraints Generation
    #--------------------------------------------------------------------------
    def _layout_info(self):
        """ Creates a dictionary from the current layout information.

        This method uses the current layout state of the component,
        comprised of constraints, clip, and hug policies, and creates
        a dictionary which can be serialized and sent to clients.

        Returns
        -------
        result : dict
            A dictionary of the current layout state for the component.

        """
        info = {
            'constraints': self._generate_constraints(),
            'resist': (self.resist_width, self.resist_height),
            'hug': (self.hug_width, self.hug_height),
        }
        return info

    def _generate_constraints(self):
        """ Creates a list of constraint info dictionaries.

        This method converts the list of symbolic constraints returned
        by the call to '_collect_constraints' into a list of constraint
        info dictionaries which can be serialized and sent to clients.

        Returns
        -------
        result : list of dicts
            A list of dictionaries which are serializable versions of
            the symbolic constraints defined for the widget.

        """
        cns = self._collect_constraints()
        cns = [cn.as_dict() for cn in expand_constraints(self, cns)]
        return cns

    def _collect_constraints(self):
        """ Creates a list of symbolic constraints for the component.

        By default, this method combines the constraints defined by
        the 'constraints' this, and those returned by a call to the
        '_hard_constraints' method. Subclasses which need more control
        should override this method.

        Returns
        -------
        result : list
            A list of symbolic constraints and deferred constraints
            for this component.

        """
        cns = self.constraints
        if not cns:
            cns = self._default_constraints()
        return cns + self._component_constraints() + self._hard_constraints()

    def _hard_constraints(self):
        """ Creates the list of required symbolic constraints.

        These are constraints that must apply to the internal layout
        computations of a component as well as that of containers which
        may parent this component. By default, all components will have
        their 'left', 'right', 'width', and 'height' symbols constrained
        to >= 0. These constraints are applied client-side, in order to
        save bandwidth. Subclasses which need to add more constraints
        should reimplement this method.

        Returns
        -------
        result : list
            A list of symbolic constraints which must always be applied
            to a component.

        """
        return []

    def _component_constraints(self):
        """ Returns a list of constraints which should be applied on
        top of any additional user-supplied constraints and hard
        constraints.

        The default implementation returns an empty list.

        """
        return []

    def _default_constraints(self):
        """ Returns a list of constraints to include if the user has
        not specified their own in the 'constraints' list.

        The default implementation returns an empty list.

        """
        return []


ABConstrainable.register(ConstraintsWidget)

