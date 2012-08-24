#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from collections import deque

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
    #: Whether or not this container should share its layout with a 
    #: parent container.
    _share_layout = False

    #: Whether or not this container owns its layout. A container which
    #: does not own its layout is not responsible for laying out its
    #: children on a resize event, and will proxy the call to its owner.
    _owns_layout = True

    #: The object which has taken ownership of the layout for this 
    #: container, if any.
    _layout_owner = None

    #: The LayoutManager instance to use for solving the layout system
    #: for this container.
    _layout_manager = None

    #: The function to use for refreshing the layout on a resize event.
    _refresh = lambda: None

    #: The table of offsets to use during a layout pass.
    _offset_table = []

    #: The table of (index, updater) pairs to use during a layout pass.
    _layout_table = []

    #: A dict mapping constraint owner id to associated LayoutBox
    _cn_owners = {}

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
        # The resized signal is connected directly to the refresh
        # method to save the overhead of the extra function call.
        self.widget().resized.connect(self.refresh)

    def init_layout(self):
        """ Initializes the layout for the container. 

        """
        super(QtContainer, self).init_layout()
        # Layout ownership can only be transferred *after* this init
        # layout method is called, since layout occurs bottom up. So,
        # we only initialize a layout manager if we are not going to
        # transfer ownership at some point.
        if not self.will_transfer():
            offset_table, layout_table = self._build_layout_table()
            cns = self._generate_constraints(layout_table)
            # Initializing the layout manager can fail if the objective 
            # function is unbounded. We let that failure occur so it can 
            # be logged. Nothing is stored until it succeeds.
            manager = LayoutManager()
            manager.initialize(cns)
            self._offset_table = offset_table
            self._layout_table = layout_table
            self._layout_manager = manager
            self._refresh = self._build_refresher(manager)
            min_size = self.compute_min_size()
            max_size = self.compute_max_size()
            widget = self.widget()
            widget.setSizeHint(min_size)
            widget.setMinimumSize(min_size)
            widget.setMaximumSize(max_size)

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
        # The _refresh function is generated on every relayout and has
        # already taken into account whether or not the container owns
        # the layout.
        self._refresh()

    def layout(self):
        """ The callback invoked by the layout manager when there are
        new layout values available.

        This iterates over the layout table and calls the geometry
        updater functions.

        """
        # We explicitly don't use enumerate() to generate the running
        # index because this method is on the code path of the resize
        # event and hence called *often*. The entire code path for a
        # resize event is micro optimized and justified with profiling.
        offset_table = self._offset_table
        layout_table = self._layout_table
        running_index = 1
        for offset_index, updater in layout_table:
            dx, dy = offset_table[offset_index]
            new_offset = updater(dx, dy)
            offset_table[running_index] = new_offset
            running_index += 1

    #--------------------------------------------------------------------------
    # Constraints Computation
    #-------------------------------------------------------------------------- 
    def _build_refresher(self, manager):
        """ A private method which will build a function which, when
        called, will refresh the layout for the container.

        Parameters
        ----------
        manager : LayoutManager
            The layout manager to use when refreshing the layout.

        """
        # The return function is a hyper optimized (for Python) closure
        # in order minimize the amount of work which is performed on the
        # code path of the resize event. This is explicitly not idiomatic
        # Python code. It exists purely for the sake of efficiency, 
        # justified with profiling.
        mgr_layout = manager.layout
        layout = self.layout
        primitive = self.layout_box.primitive
        width_var = primitive('width')
        height_var = primitive('height')
        widget = self._widget
        width = widget.width
        height = widget.height
        def refresher():
            mgr_layout(layout, width_var, height_var, (width(), height()))
        return refresher

    def _build_layout_table(self):
        """ A private method which will build the layout table for
        this container.

        A layout table is a pair of flat lists which hold the required
        objects for laying out the child widgets of this container.
        The flat table is built in advance (and rebuilt if and when
        the tree structure changes) so that it's not necessary to 
        perform an expensive tree traversal to layout the children
        on every resize event.

        Returns
        -------
        result : (list, list)
            The offset table and layout table to use during a resize
            event.
        
        """
        # The offset table is a list of (dx, dy) tuples which are the
        # x, y offsets of children expressed in the coordinates of the
        # layout owner container. This owner container may be different
        # from the parent of the widget, and so the delta offset must
        # be subtracted from the computed geometry values during layout.
        # The offset table is updated during a layout pass in breadth
        # first order.
        #
        # The layout table is a flat list of (idx, updater) tuples. The
        # idx is an index into the offset table where the given child
        # can find the offset to use for its layout. The updater is a
        # callable provided by the widget which accepts the dx, dy 
        # offset and will update the layout geometry of the widget.
        zero_offset = (0, 0)
        offset_table = [zero_offset]
        layout_table = []
        queue = deque((0, child) for child in self.children())

        # Micro-optimization: pre-fetch bound methods and store globals
        # as locals. This method is not on the code path of a resize 
        # event, but it is on the code path of a relayout. If there
        # are many children, the queue could potentially grow large.
        push_offset = offset_table.append
        push_item = layout_table.append
        push = queue.append
        pop = queue.popleft
        QtConstraintsWidget_ = QtConstraintsWidget
        QtContainer_ = QtContainer
        isinst = isinstance

        # The queue yields the items in the tree in breadth-first order
        # starting with the immediate children of this container. If a
        # given child is a container that will share its layout, then 
        # the children of that container are added to the queue to be
        # added to the layout table.
        running_index = 0
        while queue:
            offset_index, item = pop()
            if isinst(item, QtConstraintsWidget_):
                push_item((offset_index, item.geometry_updater()))
                push_offset(zero_offset)
                running_index += 1
                if isinst(item, QtContainer_):
                    if item.transfer_layout_ownership(self):
                        for child in item.children():
                            push((running_index, child))

        return offset_table, layout_table

    def _generate_constraints(self, layout_table):
        """ Creates the list of casuarius LinearConstraint objects for
        the widgets for which this container owns the layout.

        This method walks over the items in the given layout table and
        aggregates their constraints into a single list of casuarius
        LinearConstraint objects which can be given to the layout
        manager.

        Parameters
        ----------
        layout_table : list
            The layout table created by a call to _build_layout_table.

        Returns
        -------
        result : list
            The list of casuarius LinearConstraints instances to pass to
            the layout manager.

        """
        # The mapping of constraint owners and the list of constraint
        # info dictionaries provided by the Enaml widgets.
        box = self.layout_box
        cn_owners = {self.widget_id(): box}
        cn_dicts = list(self.constraints)
        cn_dicts_extend = cn_dicts.extend

        # The list of raw casuarius constraints which will be returned 
        # from this method to be added to the casuarius solver.
        raw_cns = list(self.hard_constraints())
        raw_cns_extend = raw_cns.extend

        # The first element in a layout table item is its offset index
        # which is not relevant to constraints generation.
        isinst = isinstance
        QtContainer_ = QtContainer
        for _, updater in layout_table:
            child = updater.item
            cn_owners[child.widget_id()] = child.layout_box
            raw_cns_extend(child.hard_constraints())
            if isinst(child, QtContainer_):
                if child.transfer_layout_ownership(self):
                    cn_dicts_extend(child.constraints)
                else:
                    raw_cns_extend(child.size_hint_constraints())
            else:
                raw_cns_extend(child.size_hint_constraints())
                cn_dicts_extend(child.constraints)

        # Convert the list of Enaml constraints info dicts to actual 
        # casuarius LinearConstraint objects for the solver.
        add_cn = raw_cns.append
        as_cn = as_linear_constraint
        for info in cn_dicts:
            add_cn(as_cn(info, cn_owners))

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
        owner : Declarative
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
        self._owns_layout = False
        self._layout_owner = owner
        self._layout_manager = None
        self._refresh = owner.refresh
        self._offset_table = []
        self._layout_table = []
        self._cn_owners = {} 
        return True

    def will_transfer(self):
        """ Whether or not the container expects to transfer its layout
        ownership to its parent.

        This method is predictive in nature and exists so that layout
        managers are not senslessly created during the bottom-up layout
        initialization pass. It is declared public so that subclasses 
        can override the behavior if necessary.

        """
        if self._share_layout:
            if isinstance(self.parent(), QtContainer):
                return True
        return False

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
            res = QSize(w, h)
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
            res = QSize(w, h)
        else:
            res = QSize()
        if res.width() == -1:
            res.setWidth(16777215)
        if res.height() == -1:
            res.setHeight(16777215)
        return res

