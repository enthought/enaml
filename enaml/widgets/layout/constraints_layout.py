from .layout_manager import AbstractLayoutManager

import csw


class ConstraintsLayout(AbstractLayoutManager):

    def update_constraints_if_needed(self):
        raise NotImplementedError
    
    def set_needs_update_constraints(self):
        raise NotImplementedError
    
    def update_constraints(self):
        raise NotImplementedError
    
    def layout_if_needed(self):
        raise NotImplementedError
    
    def set_needs_layout(self):
        raise NotImplementedError
    
    def layout(self):
        raise NotImplementedError

    def initialize(self, container):
        if getattr(self, '_is_initializing', False):
            return
        self._is_initializing = True
        # FIXME: Make sure all child constraint lists have been created to avoid
        # weird reentry. We should figure out why *getting* the .constraints
        # trait triggers the _constraints_changed() trait handler. But for now,
        # just trigger them early before we modify any state and rely on the
        # _is_initializing guards to avoid executing any real code.
        for child in container.children:
            child.constraints

        # Rather than do intialization in the __init__ method, which
        # in Python has the context of only happening once, we use
        # this method since the manager will be re-initialized whenever
        # any of the constraints of the containers children change.

        # (Enaml LinearConstraint -> csw.Constraint)
        self.constraints = []

        solver = self.solver = csw.SimplexSolver()
        solver.SetAutosolve(False)

        # Setup the containers constraints in the solver's table.
        # Since the children are laid out relative to the container,
        # the container's origin is set to (0, 0) for this solver.
        # Even though this container may be used in a parent solver
        # where it's origin is other than (0, 0)
        x = (container.left == 0.0)
        y = (container.top == 0.0)
        self.add_constraint(x)
        self.add_constraint(y)

        # Setup the child constraints in the solver's table
        for child in container.children:
            for constraint in child.constraints:
                self.add_constraint(constraint)
        
        # Compute the hint variables for solver iteration. Some are stronger
        # than others.
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
        
        def x_hint_getter(obj):
            return lambda: obj.pos_hint()[0]
        
        def y_hint_getter(obj):
            return lambda: obj.pos_hint()[1]

        w_var = container.width.csw_var
        if solver_contains(w_var):
            changes.append((w_var, width_getter(container), csw.sStrong()))
        
        h_var = container.height.csw_var
        if solver_contains(h_var):
            changes.append((h_var, height_getter(container), csw.sStrong()))
        
        for child in container.children:
            w_var = child.width.csw_var
            if solver_contains(w_var):
                changes.append((w_var, width_hint_getter(child), csw.sWeak()))
            
            h_var = child.height.csw_var
            if solver_contains(h_var):
                changes.append((h_var, height_hint_getter(child), csw.sWeak()))
        
        solver.SetAutosolve(True)
        self._is_initializing = False

    def add_constraint(self, constraint):
        """ Add a constraint to the solver, and keep a reference to it for
        further examination.

        """
        csw_constraint = constraint.convert_to_csw()
        self.constraints.append((constraint, csw_constraint))
        self.solver.AddConstraint(csw_constraint)

    def layout(self, container):
        if getattr(self, '_is_initializing', False):
            return
        solver = self.solver
        changes = self.changes

        if not changes:
            solver.Resolve()
            self.update_children(container)
            return
        
        for var, val_func, strength in changes:
            solver.AddEditVar(var, strength)
        
        solver.BeginEdit()

        for var, val_func, strength in changes:
            solver.SuggestValue(var, val_func())
            
        solver.Resolve()

        self.update_children(container)

        # XXX handle the case where the suggested width and height
        # led to an unsolvable system and so the computed width and
        # height are now different from the actual widget width and 
        # height.

        solver.EndEdit()

    def update_children(self, container):
        for child in container.children:
            x = child.left.csw_var.Value()
            y = child.top.csw_var.Value()
            width = child.width.csw_var.Value()
            height = child.height.csw_var.Value()
            child.set_geometry(int(x), int(y), int(width), int(height))

