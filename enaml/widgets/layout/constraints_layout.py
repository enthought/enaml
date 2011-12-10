#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from collections import defaultdict
import weakref

from .layout_manager import AbstractLayoutManager
from .layout_helpers import DeferredConstraints

import casuarius


class ConstraintsLayout(AbstractLayoutManager):

    def __init__(self, component):
        self.component = weakref.ref(component)

        # The solver instance to use for this manager
        self.solver = None

        # The constraints for the component which should never need to change
        self.component_cns = None

        # The user constraints which may change
        self.user_cns = None

        # The hard constraints for the children which should never change
        self.child_cns = None

        # The default child size constraints which will change if a 
        # a childs size_hint is updated
        self.child_size_cns = None

        # A flag to prevent recursion into various method. 
        # XXX this may no longer be needed
        self._recursion_guard = False

        # A flag to indicate whether this manager has been initialized.
        self._initialized = False

    #--------------------------------------------------------------------------
    # Initalization
    #--------------------------------------------------------------------------
    def initialize(self):
        """ Initializes the solver by creating all of the necessary 
        constraints for this components children and adding them to 
        the solver.

        """
        if self._recursion_guard or self._initialized:
            return
        self._recursion_guard = True

        # Rather than do intialization in the __init__ method, which
        # in Python has the context of only happening once, we use
        # this method since the manager will be re-initialized whenever
        # any of the constraints of the components children change.
        self.solver = casuarius.Solver(autosolve=False)
        self.component_cns = []
        self.user_cns = []
        self.child_cns = defaultdict(list)
        self.child_size_cns = defaultdict(list)

        component = self.component()
        if component is None:
            msg = 'Component weakly referenced by %r disappeared' % self
            raise RuntimeError(msg)

        solver = self.solver

        # The list of all descendants participating in constraints-based layout.
        descendants = list(self.traverse_descendants(component))

        # Disable the layout engines on all Containers descending from this one.
        # FIXME: This destructively sets the .layout attribute to None. It
        # works, but we might be able to do it more cleanly.
        for desc in descendants:
            if hasattr(desc, 'layout'):
                if type(desc.layout) is type(self):
                    desc.layout = None
                else:
                    # Initialize their layout.
                    desc.initialize_layout()

        # Component default constraints
        cns = self.compute_component_cns(component)
        self.component_cns = cns
        self.add_constraints(cns)

        # User constraints
        cns = self.compute_user_cns(component)
        for child in descendants:
            cns.extend(self.compute_user_cns(child))
        self.user_cns = cns
        self.add_constraints(cns)

        # Child default constraints
        cns_dict = self.child_cns
        for child in descendants:
            cns = self.compute_child_cns(child)
            cns_dict[child].extend(cns)
            self.add_constraints(cns)
        
        # Child size constraints
        cns_dict = self.child_size_cns
        for child in descendants:
            cns = self.compute_child_size_cns(child)
            cns_dict[child].extend(cns)
            self.add_constraints(cns)

        solver.autosolve = True

        # Set the minimum size of the component based on the current
        # set of constraints
        min_size = self.calc_min_size()
        component.set_min_size(*min_size)

        self._recursion_guard = False
        self._initialized = True

    def add_constraints(self, constraints):
        """ Add an iterable of constraints to the solver.

        """
        solver = self.solver
        for cn in constraints:
            solver.add_constraint(cn)

    #--------------------------------------------------------------------------
    # Solver Iteration
    #--------------------------------------------------------------------------
    def layout(self):
        """ Perform an iteration of the solver for the new width and 
        height of the component. This will resolve the system and update
        the geometry of all of the component's children.

        """
        if self._recursion_guard or not self._initialized:
            return
        self._recursion_guard = True

        component = self.component()
        if component is None:
            msg = 'Component weakly referenced by %r disappeared' % self
            raise RuntimeError(msg)

        solver = self.solver

        # Grab the info required for the suggestions to the solver
        width, height = component.size()
        width_var = component.width
        height_var = component.height

        with solver.suggest_values([(width_var, width), (height_var, height)], casuarius.medium):
            # Update the geometry of the children with their new
            # solved values.
            for child in self.traverse_descendants(component):
                child.set_solved_geometry(component)

        self._recursion_guard = False

    def calc_min_size(self):
        """ Run an iteration of the solver with the suggested size of the
        component set to (0, 0). This will cause the solver to effectively
        compute the minimum size that the window can be to solve the
        system. The return value is (min_width, min_height).

        """
        component = self.component()
        if component is None:
            msg = 'Component weakly referenced by %r disappeared' % self
            raise RuntimeError(msg)
        
        solver = self.solver

        width_var = component.width
        height_var = component.height

        # FIXME: here we pick a 'medium' strength like the window resize but
        # weight it a little less. Uses of 'medium' in constraints should
        # override this. In the future, we should add more meaningful Strengths.
        with solver.suggest_values([(width_var, 0.0), (height_var, 0.0)],
            default_strength=casuarius.medium, default_weight=0.1):
            min_width = width_var.value
            min_height = height_var.value

        return (min_width, min_height)

    def traverse_descendants(self, component):
        """ Do a preorder traversal of all visible descendants of the component
        that participate in the Constraints-base layout.

        """
        for child in component.children:
            if child.visible:
                yield child
                child_layout = getattr(child, 'layout', None)
                if child_layout is None or type(child_layout) is type(self):
                    for desc in self.traverse_descendants(child):
                        yield desc


    #--------------------------------------------------------------------------
    # Constraint computation
    #--------------------------------------------------------------------------
    def compute_component_cns(self, component):
        """ Computes the required constraints of the component.

        """
        cns = []
        for name in ('left', 'top', 'width', 'height'):
            cn = (getattr(component, name) >= 0)
            cns.append(cn)
        return cns

    def compute_user_cns(self, component):
        """ Computes the user supplied constraints for the component.

        """
        # XXX this is a bit of hack at the moment, since only 
        # Containers have constraints.
        if not hasattr(component, 'constraints'):
            return []
        cns = []
        user_constraints = component.constraints if component.constraints else component.default_user_constraints()
        for constraint in user_constraints + component.container_constraints():
            if isinstance(constraint, DeferredConstraints):
                cns.extend(constraint.get_constraint_list(component))
            else:
                cns.append(constraint)
        return cns
    
    def compute_child_cns(self, child):
        """ Computes the hard default constraints for a child. These
        should never change for a given child.

        """
        constraints = [
            child.width >= 0,
            child.height >= 0,
        ]
        return constraints

    def compute_child_size_cns(self, child):
        """ Computes the constraints relating the size hint of a child.
        These may change if the size hint of a child changes, or the
        values for its 'hug' or 'resist_clip' attribute changes.

        """
        constraints = []

        width_hint, height_hint = child.size_hint()
        hug_width = child.hug_width
        hug_height = child.hug_height
        resist_clip_width = child.resist_clip_width
        resist_clip_height = child.resist_clip_height

        if width_hint >= 0:
            if hug_width != 'ignore':
                cn = (child.width == width_hint) | hug_width
                constraints.append(cn)
            if resist_clip_width != 'ignore':
                cn = (child.width >= width_hint) | resist_clip_width
                constraints.append(cn)
        
        if height_hint >= 0:
            if hug_height != 'ignore':
                cn = (child.height == height_hint) | hug_height
                constraints.append(cn)
            if resist_clip_height != 'ignore':
                cn = (child.height >= height_hint) | resist_clip_height
                constraints.append(cn)

        return constraints
    
    #--------------------------------------------------------------------------
    # Constraint Update 
    #--------------------------------------------------------------------------
    def update_constraints(self):
        """ Re-run the initialization routine to build a new solver with
        updated constraints. This should typically only be called when 
        the user constraints are updated.

        """
        # FIXME: we can probably do better by storing the old constraints,
        # getting the new constraints, finding the differences, and telling the
        # solver to remove/add constraints.
        # Or maybe not. Timings will tell.
        self._initialized = False
        self.initialize()

    def update_size_cns(self, child):
        """ Update the constraints for the size hint of the given child.
        This will be more efficient that calling update_constraints
        and should be used when size_hint of child changes, or the
        it 'hug' or 'resist_clip' attributes change.

        """
        if not self._initialized:
            return
        component = self.component()
        if component is None:
            msg = 'Component weakly referenced by %r disappeared' % self
            raise RuntimeError(msg)

        solver = self.solver
        
        # Remove the existing constraints for the child's size hint.
        old_cns = self.child_size_cns[child]
        for old_cn in old_cns:
            solver.remove_constraint(old_cn)
        del self.child_size_cns[child]

        # Add the new constraints for the child's size hint
        new_cns = self.compute_child_size_cns(child)
        self.child_size_cns[child].extend(new_cns)
        for new_cn in new_cns:
            solver.add_constraint(new_cn)

        # Recompute the minimum size since the constraint changes
        # may have an effect on it.
        min_size = self.calc_min_size()
        component.set_min_size(*min_size)

