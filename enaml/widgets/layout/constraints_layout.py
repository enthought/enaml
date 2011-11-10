from collections import defaultdict
import weakref

from .layout_manager import AbstractLayoutManager
from .symbolics import STRENGTH_MAP

import csw


MEDIUM = STRENGTH_MAP['medium']

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
        self.solver = csw.SimplexSolver()
        self.component_cns = []
        self.user_cns = []
        self.child_cns = defaultdict(list)
        self.child_size_cns = defaultdict(list)

        component = self.component()
        if component is None:
            msg = 'Component weakly referenced by %r disappeared' % self
            raise RuntimeError(msg)

        solver = self.solver
        solver.SetAutosolve(False)

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

        solver.SetAutosolve(True)

        # Set the minimum size of the component based on the current
        # set of constraints
        min_size = self.calc_min_size()
        component.set_min_size(*min_size)

        self._recursion_guard = False
        self._initialized = True

    def add_constraints(self, constraints):
        """ Add an iterable of constraints in csw form to the solver.

        """
        solver = self.solver
        for cn in constraints:
            if isinstance(cn, list):
                for c in cn:
                    solver.AddConstraint(c)
            else:
                solver.AddConstraint(cn)

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
        width_var = component.width.csw_var
        height_var = component.height.csw_var

        # Add the variables we're going to edit to the solver
        solver.AddEditVar(width_var, MEDIUM)
        solver.AddEditVar(height_var, MEDIUM)

        solver.BeginEdit()

        # Suggest the new width and height of the component to 
        # the solver.
        solver.SuggestValue(width_var, width)
        solver.SuggestValue(height_var, height)
            
        solver.Resolve()

        # Update the geometry of the children with their new
        # solved values. We must do this *before* we call EndEdit
        # or else the variable values will reset to the previous 
        # unedited state.
        set_solved_geometry = self.set_solved_geometry
        for child in self.traverse_descendants(component):
            set_solved_geometry(child)
        
        solver.EndEdit()

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
            
        width_var = component.width.csw_var
        height_var = component.height.csw_var

        # Add the variables we're going to edit to the solver, we use
        # the same strength that will be used during resize iterations.
        solver.AddEditVar(width_var, MEDIUM)
        solver.AddEditVar(height_var, MEDIUM)

        solver.BeginEdit()

        # Suggest the smallest possible component size to the solver
        # so that the value it computes will be the proper minimum 
        # size of the component
        solver.SuggestValue(width_var, 0)
        solver.SuggestValue(height_var, 0)
            
        solver.Resolve()

        min_width = width_var.Value()
        min_height = height_var.Value()

        solver.EndEdit()

        return (min_width, min_height)

    def set_solved_geometry(self, component):
        """ Set the geometry of a component to its solved geometry.

        """
        x = component.left.csw_var.Value()
        y = component.top.csw_var.Value()
        width = component.width.csw_var.Value()
        height = component.height.csw_var.Value()
        x, y, width, height = (int(round(z)) for z in (x, y, width, height))
        # This is offset against the root Container. Each Component's geometry
        # actually needs to be offset against its parent. Walk up the tree and
        # subtract out the parent's offset.
        for ancestor in self.walk_up_containers(component):
            dx, dy = ancestor.pos()
            x -= dx
            y -= dy
        component.set_geometry(x, y, width, height)

    def traverse_descendants(self, component):
        """ Do a preorder traversal of all descendants of the component that
        participate in the Constraints-base layout.

        """
        for child in component.children:
            yield child
            child_layout = getattr(child, 'layout', None)
            if child_layout is None or type(child_layout) is type(self):
                for desc in self.traverse_descendants(child):
                    yield desc

    def walk_up_containers(self, component):
        """ Walk up the component hierarchy from a given node and yield the
        parent Containers, excepting the root Container.

        """
        root = self.component()
        if root is None:
            msg = 'Component weakly referenced by %r disappeared' % self
            raise RuntimeError(msg)
        parent = component.parent
        while parent is not root and parent is not None:
            yield parent
            parent = parent.parent

    #--------------------------------------------------------------------------
    # Constraint computation
    #--------------------------------------------------------------------------
    def compute_component_cns(self, component):
        """ Computes the required constraints of the component.

        """
        cns = []
        for name in ('left', 'top', 'width', 'height'):
            cn = (getattr(component, name) >= 0).convert_to_csw()
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
            cns.append(constraint.convert_to_csw())
        return cns
    
    def compute_child_cns(self, child):
        """ Computes the hard default constraints for a child. These
        should never change for a given child.

        """
        constraints = [val.convert_to_csw() for val in
                (child.width >= 0, child.height >= 0)]
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
                csw_cn = cn.convert_to_csw()
                constraints.append(csw_cn)
            if resist_clip_width != 'ignore':
                cn = (child.width >= width_hint) | resist_clip_width
                csw_cn = cn.convert_to_csw()
                constraints.append(csw_cn)
        
        if height_hint >= 0:
            if hug_height != 'ignore':
                cn = (child.height == height_hint) | hug_height
                csw_cn = cn.convert_to_csw()
                constraints.append(csw_cn)
            if resist_clip_height != 'ignore':
                cn = (child.height >= height_hint) | resist_clip_height
                csw_cn = cn.convert_to_csw()
                constraints.append(csw_cn)

        return constraints
    
    #--------------------------------------------------------------------------
    # Constraint Update 
    #--------------------------------------------------------------------------
    def update_constraints(self):
        """ Re-run the initialization routine to build a new solver with
        updated constraints. This should typically only be called when 
        the user constraints are updated.

        """
        self._initialized = False
        self.initialize()

    def update_size_cns(self, child):
        """ Update the constraints for the size hint of the given child.
        This will be more efficient that calling update_constraints
        and should be used when size_hint of child changes, or the
        it 'hug' or 'resist_clip' attributes change.

        """
        component = self.component()
        if component is None:
            msg = 'Component weakly referenced by %r disappeared' % self
            raise RuntimeError(msg)

        solver = self.solver
        
        # Remove the existing constraints for the child's size hint.
        old_cns = self.child_size_cns[child]
        for old_cn in old_cns:
            solver.RemoveConstraint(old_cn)
        del self.child_size_cns[child]

        # Add the new constraints for the child's size hint
        new_cns = self.compute_child_size_cns(child)
        self.child_size_cns[child].extend(new_cns)
        for new_cn in new_cns:
            solver.AddConstraint(new_cn)
        
        # Recompute the minimum size since the constraint changes
        # may have an effect on it.
        min_size = self.calc_min_size()
        component.set_min_size(*min_size)

