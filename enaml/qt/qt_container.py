#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from enaml.layout.layout_manager import LayoutManager

from .qt.QtCore import QSize, Signal
from .qt.QtGui import QFrame
from .qt_constraints_widget import QtConstraintsWidget, LayoutBox


def _convert_cn_info(info, owners):
    """ Converts the lhs or rhs of a linear constraint info dict into 
    its corresponding casuarius object.

    """
    cn_type = info['type']
    if cn_type == 'linear_expression':
        const = info['constant']
        terms = info['terms']
        convert = _convert_cn_info
        res = sum(convert(t, owners) for t in terms) + const
    elif cn_type == 'term':
        coeff = info['coeff']
        var = info['var']
        res = coeff * _convert_cn_info(var, owners)
    elif cn_type == 'linear_symbolic':
        sym_name = info['name'].split('-')[-1]
        owner_id = info['owner']
        owner = owners.get(owner_id, None)
        if owner is None:
            owner = owners[owner_id] = LayoutBox(info['name'], owner_id)
        res = owner.primitive(sym_name)
    else:
        msg = 'Unhandled constraint info type `%s`' % cn_type
        raise ValueError(msg)
    return res


def as_linear_constraint(info, owners):
    """ Converts a constraint info dict into a casuarius linear
    constraint.

    For constraints specified in the info dict which do not have a 
    corresponding owner (e.g. those created by box helpers) a 
    constraint variable will be synthesized.

    Parameters
    ----------
    info : dict
        A dictionary sent from an Enaml widget which specifies the
        information for a linear constraint.

    owners : dict
        A mapping from constraint id to an owner object which holds
        the actual casuarius constraint variables as attributes.

    Returns
    -------
    result : LinearConstraint
        A casuarius linear constraint for the given dict.

    """
    if info['type'] != 'linear_constraint':
        msg = 'The info dict does not specify a linear constraint.'
        raise ValueError(msg)
    convert = _convert_cn_info
    lhs = convert(info['lhs'], owners)
    rhs = convert(info['rhs'], owners)
    op = info['op']
    if op == '==':
        cn = lhs == rhs
    elif op == '<=':
        cn = lhs <= rhs
    elif op == '>=':
        cn = lhs >= rhs
    else:
        msg = 'Unhandled constraint operator `%s`' % op
        raise ValueError(msg)
    return cn | info['strength'] | info['weight']


class QContainer(QFrame):
    """ A subclass of QFrame which behaves as a container.

    """
    #: A signal which is emitted on a resize event.
    resized = Signal()

    #: An invalid QSize used as the default value for class instances.
    _size_hint = QSize()

    def resizeEvent(self, event):
        """ Converts a resize event into a signal.

        """
        super(QContainer, self).resizeEvent(event)
        self.resized.emit()

    def sizeHint(self):
        """ Returns the previously set size hint. If that size hint is
        invalid, the superclass' sizeHint will be used.

        """
        hint = self._size_hint
        if not hint.isValid():
            hint = super(QContainer, self).sizeHint()
        return hint

    def setSizeHint(self, hint):
        """ Sets the size hint to use for this widget.

        """
        self._size_hint = hint

    def minimumSizeHint(self):
        """ Returns the minimum size hint of the widget.

        The minimum size hint for a QContainer is conceptually the same
        as its size hint, so we just return that value.

        """
        return self.sizeHint()


class QtContainer(QtConstraintsWidget):
    """ A Qt implementation of an Enaml Container.

    """
    #--------------------------------------------------------------------------
    # Setup Methods
    #--------------------------------------------------------------------------
    def create_widget(self, parent, tree):
        """ Creates the underlying QContainer widget.

        """
        return QContainer(parent)

    def create(self, tree):
        """ Create and initialize the underlying widget.

        """
        super(QtContainer, self).create(tree)
        self._share_layout = tree['layout']['share_layout']
        self._cn_owners = None
        self._owns_layout = True
        self._layout_owner = None
        self._layout_manager = None
        widget = self.widget()
        widget.resized.connect(self.on_resize)

    def init_layout(self):
        """ Initializes the layout for the container. 

        """
        super(QtContainer, self).init_layout()
        widget = self.widget()
        self._is_show = widget.isVisible()
        if self._owns_layout:
            mgr = self._layout_manager = LayoutManager()
            mgr.initialize(self._generate_constraints())
            min_size = self.compute_min_size()
            max_size = self.compute_max_size()
            widget.setSizeHint(min_size)
            widget.setMinimumSize(min_size)
            widget.setMaximumSize(max_size)

    #--------------------------------------------------------------------------
    # Signal Handlers
    #--------------------------------------------------------------------------
    def on_resize(self):
        """ The signal handler for the 'resized' signal.

        This handler triggers a layout pass when the container widget 
        is resized.

        """
        if self._layout_manager is not None:
            self.refresh()

    #--------------------------------------------------------------------------
    # Layout Handling
    #--------------------------------------------------------------------------
    def relayout(self):
        """ Rebuilds the constraints layout for this widget if it owns
        the responsibility for laying out its descendents.

        """
        if self._owns_layout:
            self.init_layout()
            self.refresh()
        else:
            self._layout_owner.relayout()
            
    def refresh(self):
        """ Makes a layout pass over the descendents if this widget owns
        the responsibility for their layout.

        """
        if self._owns_layout:
            primitive = self.layout_box.primitive
            width = primitive('width', False)
            height = primitive('height', False)
            widget = self.widget()
            size = (widget.width(), widget.height())
            self._layout_manager.layout(self.layout, width, height, size)
        else:
            self._layout_owner.refresh()

    def layout(self):
        """ The callback invoked by the layout manager when there are
        new layout values available. 

        This traverses the children for which this container has layout 
        ownership and applies the geometry updates.

        """
        stack = [((0, 0), self.children())]
        pop = stack.pop
        push = stack.append
        while stack:
            offset, children = pop()
            for child in children:
                new_offset = child.update_layout_geometry(*offset)
                if isinstance(child, QtContainer):
                    if child._layout_owner is self:
                        push((new_offset, child.children()))

    #--------------------------------------------------------------------------
    # Constraints Computation
    #--------------------------------------------------------------------------
    def _generate_constraints(self):
        """ Creates the list of casuarius LinearConstraint objects for
        the widgets for which this container owns the layout.

        This method descends the tree for all containers and children 
        for which this container can manage layout, and aggregates all 
        of their constraints into a single list of LinearConstraint
        objects which can be given to the layout manager.

        """
        # The mapping of constraint owners and the list of constraint
        # info dictionaries provided by the Enaml widgets.
        box = self.layout_box
        cn_owners = {self.widget_id(): box}
        cn_dicts = list(self.constraints)
        cn_dicts_extend = cn_dicts.extend

        # The list of raw casuarius constraints which will be returned 
        # from this method to be added to the casuarius solver.
        raw_cns = []
        raw_cns_extend = raw_cns.extend
        
        # The widget descendent traversal stack
        stack = list(self.children())
        stack_pop = stack.pop
        stack_extend = stack.extend

        # While traversing the tree, the provided Enaml constraints and
        # size hint constraints are collected from leaf children. For
        # container children, this container attempts to usurp layout
        # ownership. If the takeover is successful, the new children are
        # recursively descended. Otherwise, the child is treated as a
        # leaf. The constraint owners map is populated during traversal
        # so that the real casuarius constraints can be generated.
        while stack:
            child = stack_pop()
            if isinstance(child, QtConstraintsWidget):
                child_box = child.layout_box
                cn_owners[child.widget_id()] = child_box
                if isinstance(child, QtContainer):
                    if child.transfer_layout_ownership(self):
                        cn_dicts_extend(child.constraints)
                        stack_extend(child.children())
                    else:
                        raw_cns_extend(child.size_hint_constraints())
                else:
                    raw_cns_extend(child.size_hint_constraints())
                    cn_dicts_extend(child.constraints)

        # Convert the list of Enaml constraints info dicts to actual 
        # casuarius LinearConstraint objects for the solver.
        add_cn = raw_cns.append
        for info in cn_dicts:
            add_cn(as_linear_constraint(info, cn_owners))

        # We keep a strong reference to the constraint owners dict,
        # since it may include instances of LayoutBox which were 
        # created on-the-fly and hold constraint variables which 
        # should not be deleted.
        self._cn_owners = cn_owners

        return raw_cns

    #--------------------------------------------------------------------------
    # Auxiliary Methods
    #--------------------------------------------------------------------------
    def transfer_layout_ownership(self, owner):
        """ A method which can be called by other components in the
        hierarchy to gain ownership responsibility for the layout 
        of the children of this container. By default, the transfer
        is allowed and is the mechanism which allows constraints to
        cross widget boundaries. Subclasses should reimplement this 
        method if different behavior is desired.

        Parameters
        ----------
        owner : BaseComponent
            The component which has taken ownership responsibility
            for laying out the children of this component. All 
            relayout and refresh requests will be forwarded to this
            component.
        
        Returns
        -------
        results : bool
            True if the transfer was allowed, False otherwise.
        
        """
        if not self._share_layout:
            return False
        self._cn_owners = None
        self._owns_layout = False
        self._layout_owner = owner
        self._layout_manager = None
        return True

    def compute_min_size(self):
        """ Calculates the minimum size of the container which would 
        allow all constraints to be satisfied. 

        If this container does not own its layout then it will return 
        an invalid QSize.

        Returns
        -------
        result : QSize
            A (potentially) invalid QSize which is the minimum size 
            required to satisfy all constraints.

        """
        if self._owns_layout and self._layout_manager is not None:
            primitive = self.layout_box.primitive
            width = primitive('width')
            height = primitive('height')
            w, h = self._layout_manager.get_min_size(width, height)
            res = QSize(int(round(w)), int(round(h)))
        else:
            res = QSize()
        return res

    def compute_max_size(self):
        """ Calculates the maximum size of the container which would 
        allow all constraints to be satisfied. 

        If this container does not own its layout then it will return 
        an invalid QSize.

        Returns
        -------
        result : QSize
            A (potentially) invalid QSize which is the maximum size 
            allowable while still satisfying all constraints.

        """
        if self._owns_layout and self._layout_manager is not None:
            primitive = self.layout_box.primitive
            width = primitive('width')
            height = primitive('height')
            w, h = self._layout_manager.get_max_size(width, height)
            res = QSize(int(round(w)), int(round(h)))
        else:
            res = QSize()
        if res.width() == -1:
            res.setWidth(16777215)
        if res.height() == -1:
            res.setHeight(16777215)
        return res

