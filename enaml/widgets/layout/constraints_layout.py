import weakref

from .layout_manager import AbstractLayoutManager

import csw


class ConstraintsLayout(AbstractLayoutManager):

    def __init__(self, component):
        self.component = weakref.ref(component)
        self.solver = None

        # Flag to note that we are currently in the initialize() method and
        # should not re-enter.
        self._is_initializing = False
    
    def update_constraints(self):
        # FIXME: we should be able to do less than a full initialization.
        self.initialize()
    
    def initialize(self):
        if self._is_initializing:
            return
        self._is_initializing = True

        # Rather than do intialization in the __init__ method, which
        # in Python has the context of only happening once, we use
        # this method since the manager will be re-initialized whenever
        # any of the constraints of the components children change.
        component = self.component()
        if component is None:
            msg = 'Component weakly referenced by %r disappeared' % self
            raise RuntimeError(msg)

        # (LinearConstraint, csw.Constraint)
        self.constraints = []

        solver = self.solver = csw.SimplexSolver()
        solver.SetAutosolve(False)

        # Setup the components constraints in the solver's table.
        # Since the children are laid out relative to the component,
        # the component's origin is set to (0, 0) for this solver.
        # Even though this component may be used in a parent solver
        # where it's origin is other than (0, 0)
        x = (component.left == 0.0)
        y = (component.top == 0.0)
        self.add_constraint(x)
        self.add_constraint(y)

        # Setup the child constraints in the solver's table
        for child in component.children:
            for constraint in child.constraints:
                self.add_constraint(constraint)

        # Compute the hint variables for solver iteration. 
        # Some are stronger than others.
        self.changes = changes = []
        solver_contains = solver.FContainsVariable

        def width_getter(obj):
            return lambda: obj.size()[0]
        
        def height_getter(obj):
            return lambda: obj.size()[1]
        
        def width_hint_getter(obj):
            return lambda: obj.size_hint()[0]
        
        def height_hint_getter(obj):
            return lambda: obj.size_hint()[1]

        w_var = component.width.csw_var
        if solver_contains(w_var):
            changes.append((w_var, width_getter(component), csw.sMedium()))
        
        h_var = component.height.csw_var
        if solver_contains(h_var):
            changes.append((h_var, height_getter(component), csw.sMedium()))
        
        for child in component.children:
            if child.style_id == 'pb':
                print width_hint_getter(child)(), height_hint_getter(child)()
            w_var = child.width.csw_var
            if solver_contains(w_var):
                changes.append((w_var, width_hint_getter(child), csw.sWeak()))
            
            h_var = child.height.csw_var
            if solver_contains(h_var):
                changes.append((h_var, height_hint_getter(child), csw.sWeak()))

        solver.SetAutosolve(True)

        self._is_initializing = False

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
            self.constraints.append((constraint, csw_constraint))
            self.solver.AddConstraint(csw_constraint)

    def layout(self):
        component = self.component()
        if component is None:
            msg = 'Component weakly referenced by %r disappeared' % self
            raise RuntimeError(msg)

        if self._is_initializing:
            return

        solver = self.solver
        changes = self.changes

        if not changes:
            solver.Resolve()
            set_solved_geometry = self.set_solved_geometry
            for child in component.children:
                set_solved_geometry(child)
            return
        
        for var, val_func, strength in changes:
            solver.AddEditVar(var, strength)
        
        solver.BeginEdit()

        for var, val_func, strength in changes:
            solver.SuggestValue(var, val_func())
            
        solver.Resolve()

        set_solved_geometry = self.set_solved_geometry
        for child in component.children:
            set_solved_geometry(child)

        solver.EndEdit()

    def set_solved_geometry(self, component):
        """ Set the geometry of a Component to its solved geometry.

        """
        x = component.left.csw_var.Value()
        y = component.top.csw_var.Value()
        width = component.width.csw_var.Value()
        height = component.height.csw_var.Value()
        args = (int(round(z)) for z in (x, y, width, height))
        component.set_geometry(*args)

