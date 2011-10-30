import weakref

from .layout_manager import AbstractLayoutManager
from .symbolics import STRENGTH_MAP

import csw


MEDIUM = STRENGTH_MAP['medium']


class ConstraintsLayout(AbstractLayoutManager):

    def __init__(self, component):
        self.component = weakref.ref(component)
        self.solver = csw.SimplexSolver()
        self._recursion_guard = False
    
    def update_constraints(self):
        # FIXME: we should be able to do less than a full initialization.
        pass

    def initialize(self):
        if self._recursion_guard:
            return
        self._recursion_guard = True

        # Rather than do intialization in the __init__ method, which
        # in Python has the context of only happening once, we use
        # this method since the manager will be re-initialized whenever
        # any of the constraints of the components children change.
        component = self.component()
        if component is None:
            msg = 'Component weakly referenced by %r disappeared' % self
            raise RuntimeError(msg)

        solver = self.solver
        solver.SetAutosolve(False)

        # The default required constraints of the component
        self.add_constraint(component.left >= 0)
        self.add_constraint(component.top >= 0)
        self.add_constraint(component.width >= 0)
        self.add_constraint(component.height >= 0)
        
        # The user supplied constraints
        for constraint in component.constraints:
            self.add_constraint(constraint)
        
        # The default constraints computed from the children
        for child in component.children:

            # Required defaults
            self.add_constraint(child.width >= 0)
            self.add_constraint(child.height >= 0)

            # Size constraints XXX need a way to update when 
            # size hint changes
            width_hint, height_hint = child.size_hint()
            width_hug, height_hug = child.hug
            width_compress, height_compress = child.compress

            if width_hint >= 0:
                cn = (child.width == width_hint) | width_hug
                self.add_constraint(cn)
                cn = (child.width >= width_hint) | width_compress
                self.add_constraint(cn)
            
            if height_hint >= 0:
                cn = (child.height == height_hint) | height_hug
                self.add_constraint(cn)
                cn = (child.height >= height_hint) | height_compress
                self.add_constraint(cn)

        solver.SetAutosolve(True)

        self._recursion_guard = False

    def add_constraint(self, constraint):
        """ Add a LinearConstraint or MultiConstraint to the solver, 
        and keep a reference to it for further examination.

        """
        if hasattr(constraint, 'constraints'):
            # This object actually holds multiple constraints.
            for sub_constraint in constraint.constraints:
                self.add_constraint(sub_constraint)
        else:
            csw_constraint = constraint.convert_to_csw()
            self.solver.AddConstraint(csw_constraint)

    def layout(self):
        if self._recursion_guard:
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

        solver.SuggestValue(width_var, width)
        solver.SuggestValue(height_var, height)
            
        solver.Resolve()

        # Gather all the computed results *before* we end the 
        # edit or the system will revert to the unedited state
        set_solved_geometry = self.set_solved_geometry
        for child in component.children:
            set_solved_geometry(child)
        
        new_width = width_var.Value()
        new_height = height_var.Value()

        solver.EndEdit()

        # Determine whether the window has been resized 
        # too small and resize it to an appropriate size.
        needs_resize = False
        if new_width > width:
            needs_resize = True
            width = new_width
        if new_height > height:
            needs_resize = True
            height = new_height
        if needs_resize:
            component.resize(width, height)

        self._recursion_guard = False

    def set_solved_geometry(self, component):
        """ Set the geometry of a Component to its solved geometry.

        """
        x = component.left.csw_var.Value()
        y = component.top.csw_var.Value()
        width = component.width.csw_var.Value()
        height = component.height.csw_var.Value()
        args = (int(round(z)) for z in (x, y, width, height))
        component.set_geometry(*args)

