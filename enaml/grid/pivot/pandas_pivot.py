""" Dynamic pivot tables using pandas.
"""

from __future__ import absolute_import

from collections import defaultdict
import csv
from cStringIO import StringIO
from itertools import izip, product
import math
import warnings

import numpy as np
import pandas

from traits.api import (Any, Bool, Dict, Either, Enum, Event, HasTraits,
    Instance, Int, List, NO_COMPARE, Property, PrototypedFrom, Set, Str, Tuple,
    Undefined, Unicode, WeakRef, cached_property, on_trait_change)

from . import expression_context
from .aggregations import agg_funcs


def format_aggregate(aggregate):
    """ The default string formatting for an aggregate.
    """
    column, aggfunc = aggregate
    if not isinstance(aggfunc, basestring):
        name = getattr(aggfunc, '__name__', None)
        if name is not None:
            aggfunc = name
        else:
            aggfunc = unicode(aggfunc)
    return u'{0} of {1}'.format(aggfunc, column)

def format_path(path):
    """ Format a Node path tuple as a string.
    """
    return u' : '.join(map(unicode, path))


class Node(HasTraits):
    """ A node in the tree of one axis.
    """

    # The value the Node represents.
    value = Any()

    # The children of this Node.
    children = List()

    # The path from the root to this Node.
    path = Tuple()

    # The depth of the Node in the tree.
    depth = Int(0)

    # Whether this Node is expanded or not.
    expanded = Bool(False)

    # The parent of this Node.
    parent = WeakRef()

    # The text for the node. Usually derived from the value but can be
    # overridden.
    text = Property(Unicode, depends_on=['value', '_text'])
    _text = Unicode(Undefined)
    @cached_property
    def _get_text(self):
        if self._text is not Undefined:
            return self._text
        else:
            return unicode(self.value)
    def _set_text(self, text):
        self._text = text


    def add_path(self, postpath):
        """ Add a path to the tree at this level.

        Parameters
        ----------
        path : tuple
            The child path.
        """
        if postpath == ():
            return
        value = postpath[0]
        path = self.path + (value,)
        postpath = postpath[1:]
        for child in self.children:
            if child.value == value:
                break
        else:
            # Make a new child.
            child = Node(value=value, parent=self, path=path,
                depth=self.depth+1)
            self.children.append(child)
        child.add_path(postpath)

    def traverse_leaves(self):
        """ Yield all of the visible leaf Nodes in depth-first order.
        """
        if not self.expanded or len(self.children) == 0:
            yield self
        else:
            for child in self.children:
                for leaf in child.traverse_leaves():
                    yield leaf

    @classmethod
    def tree_from_multiindex(cls, multiindex):
        """ Create a rooted tree from a properly sorted pandas MultiIndex.
        """
        root = cls(expanded=True)
        for path in multiindex:
            root.add_path(path)
        return root

    def expand_all(self):
        """ Expand this Node and all sub-Nodes.
        """
        if len(self.children) > 0:
            self.expanded = True
            for child in self.children:
                child.expand_all()

    def find_by_path(self, path):
        """ Find the Node corresponding to this path.
        """
        if path == ():
            return self
        value = path[0]
        subpath = path[1:]
        for child in self.children:
            if child.value == value:
                return child.find_by_path(subpath)
        else:
            raise ValueError("Could not find Node corresponding to path {0!r}".format(path))

    def expand_along_path(self, path, expanded=True):
        """ Expand Nodes along the given path.

        A value of None in the path implies that all Nodes at that level should
        be expanded.
        """
        if path == ():
            self.expanded = expanded
            return
        value = path[0]
        subpath = path[1:]
        for child in self.children:
            if value is None or child.value == value:
                if len(child.children) > 0:
                    child.expanded = expanded
                    child.expand_along_path(subpath)
                if value is not None:
                    break
        else:
            if value is not None:
                raise ValueError("Could not find Node corresponding to {0!r}".format(value))

    def ancestors(self):
        """ Return all ancestors starting from the just below the root.
        """
        node = self.parent
        ancestors = []
        if node is None:
            return ancestors
        while node.parent is not None:
            ancestors.append(node)
            node = node.parent
        return ancestors[::-1]

    def add_margins_to_subtree(self, before=True):
        """ Add margin nodes to all nodes with children.

        Parameters
        ----------
        before : bool, optional
            Whether to place the margin node before or after the other
            children.
        """
        all_nodes = []
        stack = [self]
        while stack:
            node = stack.pop()
            if len(node.children) > 0:
                stack.extend(node.children)
                all_nodes.append(node)
        if before:
            for node in all_nodes:
                node.children.insert(0, MarginNode(parent=node))
        else:
            for node in all_nodes:
                node.children.append(MarginNode(parent=node))

    def __repr__(self):
        return '<{0.__name__}: {1.text}>'.format(type(self), self)

class MarginNode(Node):
    """ A special Node that represents a margin aggregation of its
    siblings.

    It should have the same path as its parent.
    """

    text = Unicode('Total')
    path = PrototypedFrom('parent')
    depth = PrototypedFrom('parent')


class AggregationNode(Node):
    """ A special Node for holding the top-level aggregation in the column
    header.
    """

    path = PrototypedFrom('parent')
    depth = PrototypedFrom('parent')

    text = Property(Unicode, depends_on=['value'])
    @cached_property
    def _get_text(self):
        return format_aggregate(self.value)


class HeaderEvent(HasTraits):
    """ Event notifying that a Header has changed.
    """
    # The indices that the old leaves spanned.
    old_span = Tuple(Int, Int)

    # The old leaf Nodes.
    old_leaves = List(Instance(Node))

    # The new leaf Nodes that take their place.
    new_leaves = List(Instance(Node))


class Header(HasTraits):
    """ A hierarchical header.
    """
    # The root of the tree.
    root = Instance(Node)

    # Pairs of (column, aggregation) pairs.
    # If this is not empty, then AggregationNodes will be added to the
    # leaves of the tree to form the real leaf list. Only one of the
    # Headers should have a non-empty list.
    aggregates = List(Tuple(Str, Any))

    # The leaf Nodes in order.
    leaves = List(Instance(Node))

    # Maps from Nodes to their inclusive spans.
    span_left = Dict(Instance(Node), Int)
    span_right = Dict(Instance(Node), Int)

    # The leaf paths in order.
    paths = List(Tuple)

    # The unique depths of each leaf.
    depths = Set(Int)

    # An Event notifying that a structure-changing operation has
    # happened on the Header.
    update = Event(Instance(HeaderEvent))

    def update_span_map(self):
        """ Update the span map with the current leaves.
        """
        rightmost = len(self.leaves)
        span_left = defaultdict(lambda:rightmost)
        span_right = defaultdict(int)
        for i, leaf in enumerate(self.leaves):
            span_left[leaf] = i
            span_right[leaf] = i
            node = leaf.parent
            while node is not None:
                span_left[node] = min(span_left[node], i)
                span_right[node] = max(span_right[node], i)
                node = node.parent
        self.trait_set(
            span_left = span_left,
            span_right = span_right,
        )

    def get_expanded_paths(self):
        """ Return the list of paths that are currently expanded.
        """
        leaf_parents = set()
        for leaf in self.leaves:
            leaf_parents.add(leaf.parent)
        expanded_paths = sorted(n.path for n in leaf_parents)
        return expanded_paths

    def set_expanded_paths(self, expanded_paths):
        """ Expand along the given paths, ignoring missing nodes.
        """
        for path in expanded_paths:
            try:
                self.root.expand_along_path(path)
            except ValueError:
                pass

    def expand_to_depth(self, depth):
        """ Expand to a given depth.
        """
        self.root.expand_along_path((None,) * depth)

    # FIXME: refactor the common preambles and postambles out of the
    # sort_by_key() and the expand_or_collapse() methods.

    def sort_by_key(self, key, root=None):
        """ Sort each level in the (sub)tree by a given key.

        Parameters
        ----------
        key : callable
            A key-function suitable for list.sort(key=...).
        root : Node, optional
            The root of the subtree to sort. If not provided, then the
            Header's root will be used.
        """
        if root is None:
            root = self.root
        leaves = self.leaves[:]
        i = self.span_left[root]
        j = self.span_right[root] + 1
        # FIXME: I'm not sure if we really need the old leaves in order,
        # but it's part of the HeaderEvent interface and shouldn't cost
        # much to provide.
        old_leaves = leaves[i:j]

        # Do the sorting.
        # FIXME: This is a naive strategy that sorts all subtrees, even
        # the currently undisclosed ones. This may cause an extraneous
        # filling of the cache. This could be resolved by not sorting
        # collapsed Nodes and sorting them as they get opened.
        stack = [root]
        while stack:
            node = stack.pop()
            if node.children:
                node.children.sort(key=key)
                # FIXME: Does depth-first or breadth-first matter?
                stack.extend([x for x in node.children if x.children])

        new_leaves = self._get_leaves(root)
        leaves[i:j] = new_leaves
        old_span = (i, j)
        update = HeaderEvent(old_span=old_span, old_leaves=old_leaves,
            new_leaves=new_leaves)
        self.leaves = leaves
        self.update_span_map()
        self.update = update

    @on_trait_change('root:children*:expanded')
    def expand_or_collapse(self, node, name, old, expanded):
        """ Expand or collapse a node.
        """
        assert name == 'expanded'
        i = self.span_left[node]
        j = self.span_right[node] + 1
        new_leaves = self._get_leaves(node)
        leaves = self.leaves[:]
        old_leaves = leaves[i:j]
        leaves[i:j] = new_leaves
        old_span = (i, j)

        update = HeaderEvent(old_span=old_span,
            old_leaves=old_leaves, new_leaves=new_leaves)
        self.leaves = leaves
        self.update_span_map()
        self.update = update

    def handle_event(self, event):
        """ Handle the expansion or collapse of a Node.
        """
        leaves = self.leaves[:]
        leaves[event.old_span[0]:event.old_span[1]] = event.new_leaves
        self.leaves = leaves
        self.update_span_map()

    def _get_leaves(self, node):
        """ Get a list of the leaves under the given Node.

        This includes AggregationNodes, if required.
        """
        node_leaves = list(node.traverse_leaves())
        if self.aggregates:
            new_leaves = []
            for leaf_parent in node_leaves:
                for aggregate in self.aggregates:
                    new_leaves.append(AggregationNode(
                        parent=leaf_parent,
                        value=aggregate,
                    ))
            return new_leaves
        else:
            return node_leaves


    @on_trait_change('root')
    def _initial_root(self, new):
        if new is not None:
            old_expanded_paths = self.get_expanded_paths()
            self.leaves = self._get_leaves(new)
            self.set_expanded_paths(old_expanded_paths)
        else:
            self.leaves = []
        self.update_span_map()

    @on_trait_change('leaves,leaves_items')
    def _reset_paths(self):
        self.trait_set(
            paths=[x.path for x in self.leaves],
            depths=set(x.depth for x in self.leaves),
        )


class PandasEngine(HasTraits):
    """ Dynamic pivot tables using pandas.
    """

    # The original pandas DataFrame with columns of data.
    frame = Any()

    # The frame with any filters and expressions applied to it.
    filtered_frame = Any(comparison_mode=NO_COMPARE)
    def _filtered_frame_default(self):
        return self.frame

    # Pairs of (column, aggregation) pairs.
    aggregates = List(Tuple(Str, Any))

    # Which axis are the aggregates displayed on.
    aggregates_on = Enum('cols', 'rows')

    # The pivot names.
    row_pivots = List(Str)
    col_pivots = List(Str)

    # List of (name, value_or_expr) pairs of extra columns to add to the
    # data frame.
    extra_columns = List(Tuple(Str, Any))

    # A filter expression.
    filter_expr = Str('')

    # The headers on each axis.
    row_header = Instance(Header)
    col_header = Instance(Header)

    # Add margins to the rows/columns.
    row_margins = Enum(None, 'before', 'after')
    col_margins = Enum(None, 'before', 'after')

    # Extra names to add to the namespace for evaluating expressions.
    extra_ns = Dict({})

    # Paths that are expanded along for each header.
    row_expanded_paths = List(Tuple)
    col_expanded_paths = List(Tuple)

    # How deep should each axis be expanded initially.
    row_expand_depth = Int(0)
    col_expand_depth = Int(0)

    # The current sort across either axis.
    # (aggregate, path, ascending)
    row_current_sort = Either(None, Tuple(Tuple, Tuple, Bool))
    col_current_sort = Either(None, Tuple(Tuple, Tuple, Bool))

    # Whether to show the fold depth by shading.
    shade_depth = Bool(False)

    # The shape of the data.
    shape = Property(Tuple(Int, Int), depends_on=['update'])
    @cached_property
    def _get_shape(self):
        return (len(self.row_header.leaves), len(self.col_header.leaves))

    # The maximum depth a cell can be unfolded.
    max_depth = Property(Int, depends_on=['row_pivots', 'col_pivots'])
    @cached_property
    def _get_max_depth(self):
        return len(self.row_pivots) + len(self.col_pivots)

    # Fired when the structure changes.
    update = Event()

    # Another engine that is partnered to this one and shares its headers.
    buddy = WeakRef()

    # The pivot table cache.
    # Maps ((column, aggregation), row_depth, col_depth) to a pandas pivot table.
    _pivot_tables = Dict(Tuple(Any, Int, Int), Any)

    # Whether this engine should reset its headers.
    _do_reset_headers = Bool(True)


    @classmethod
    def from_frame(cls, frame, aggregates, row_pivots, col_pivots, **traits):
        """ Typical use case for instantiation.
        """
        self = cls(aggregates=aggregates, row_pivots=row_pivots,
            col_pivots=col_pivots, **traits)
        self.frame = frame
        self.row_header.expand_to_depth(self.row_expand_depth)
        self.col_header.expand_to_depth(self.col_expand_depth)
        self.row_header.set_expanded_paths(self.row_expanded_paths)
        self.col_header.set_expanded_paths(self.col_expanded_paths)
        return self

    @classmethod
    def compare(cls, frame1, frame2, aggregates, row_pivots, col_pivots, **traits):
        """ Create two PandasEngines comparing two different frames with the
        same headers.
        """
        engine1 = cls(frame=frame1, aggregates=aggregates,
            row_pivots=row_pivots, col_pivots=col_pivots, **traits)
        for name, value_or_expr in engine1.extra_columns:
            engine1.add_column(name, value_or_expr)
        engine2 = cls(frame=frame2, aggregates=aggregates,
            row_pivots=row_pivots, col_pivots=col_pivots,
            _do_reset_headers=False, **traits)
        for name, value_or_expr in engine2.extra_columns:
            engine2.add_column(name, value_or_expr)

        # engine1 will take charge of the headers.
        engine1.buddy = engine2
        engine1.refilter()
        engine2.refilter()
        engine1.row_header.expand_to_depth(engine1.row_expand_depth)
        engine1.col_header.expand_to_depth(engine1.col_expand_depth)
        engine1.row_header.set_expanded_paths(engine1.row_expanded_paths)
        engine1.col_header.set_expanded_paths(engine1.col_expanded_paths)

        return engine1, engine2

    def reset_headers(self):
        """ Reevaluate the headers.
        """
        if not self._do_reset_headers:
            return

        row_root = Node(expanded=True)
        col_root = Node(expanded=True)
        for aggregate in self.aggregates:
            tables = [self._get_pivot_table(aggregate, len(self.row_pivots),
                len(self.col_pivots))]
            if self.buddy is not None:
                # Get the associated pivot table from the buddy, too. We want to
                # have the union of paths between the two of them.
                tables.append(self.buddy._get_pivot_table(aggregate,
                    len(self.row_pivots), len(self.col_pivots)))
            for pt in tables:
                if isinstance(pt.index, pandas.MultiIndex):
                    for path in pt.index:
                        row_root.add_path(path)
                else:
                    for item in pt.index:
                        row_root.add_path((item,))
                if isinstance(pt.columns, pandas.MultiIndex):
                    for path in pt.columns:
                        col_root.add_path(path)
                else:
                    for item in pt.columns:
                        col_root.add_path((item,))

        if self.aggregates_on == 'cols':
            row_traits = dict()
            col_traits = dict(aggregates=self.aggregates)
        else:
            row_traits = dict(aggregates=self.aggregates)
            col_traits = dict()

        if self.row_margins is not None:
            row_root.add_margins_to_subtree(self.row_margins == 'before')
        row_expanded_paths = None
        if self.row_header is not None:
            row_expanded_paths = self.row_header.get_expanded_paths()
        self.row_header = Header(**row_traits)
        self.row_header.root = row_root
        if row_expanded_paths is not None:
            self.row_header.set_expanded_paths(row_expanded_paths)
        if self.buddy is not None:
            self.buddy.row_header = self.row_header

        if self.col_margins is not None:
            col_root.add_margins_to_subtree(self.col_margins == 'before')
        col_expanded_paths = None
        if self.col_header is not None:
            col_expanded_paths = self.col_header.get_expanded_paths()
        self.col_header = Header(**col_traits)
        self.col_header.root = col_root
        if col_expanded_paths is not None:
            self.col_header.set_expanded_paths(col_expanded_paths)
        if self.buddy is not None:
            self.buddy.col_header = self.col_header

    def evaluate(self, expr):
        """ Evaluate an expression in the context of the DataFrame.
        """
        ns = expression_context.__dict__.copy()
        ns.update(self.extra_ns)
        for column in self.frame.columns:
            ns[column] = self.frame[column]
        value = eval(expr, ns)
        return value

    def add_column(self, name, value_or_expr):
        """ Add a named column to the original dataset.

        Parameters
        ----------
        name : str
            The name of the new column.
        value_or_expr : array_like or str
            An array of the right shape or an expression to be evaluated
            in the context of the other columns. E.g. if A and B are
            already columns, then "A*B" is a valid expression.
        """
        if isinstance(value_or_expr, basestring):
            value_or_expr = self.evaluate(value_or_expr)
        self.frame[name] = value_or_expr

    def refilter(self):
        """ Re-apply the filters.

        Returns True if the filter has been applied and False if it
        failed.
        """
        if self.filter_expr.strip() == '':
            self.filtered_frame = self.frame
        else:
            try:
                mask = self.evaluate(self.filter_expr)
                assert np.issubdtype(mask.dtype, bool)
                self.filtered_frame = self.frame[mask]
                return True
            except Exception, e:
                msg = "Exception while evaluating {0!r}:\n{1.__name__}: {2}".format(
                    self.filter_expr, type(e), e)
                warnings.warn(msg)
                return False

    def data(self, row, col):
        """ Given integer row,col indices, return the data for that point.
        """
        aggregate, row_path, col_path = self._get_aggregate_paths(row, col)
        return self._get_value_by_paths(aggregate, row_path, col_path)

    def fold_depth(self, row, col):
        """ Given integer row,col indices, return the number of levels of
        aggregation have been done for the cell.

        A fold depth of 0 corresponds to the most a cell can be expanded.
        """
        row_path = self.row_header.paths[row]
        col_path = self.col_header.paths[col]
        return self.max_depth - len(row_path) - len(col_path)

    def get_path_to_cell(self, row, col):
        """ Return the path to the given cell as strings for display.

        Parameters
        ----------
        row, col : int
            The indices of the cell.

        Returns
        -------
        agg_column : str
            The aggregated column.
        agg_func : str
            The name of the aggregation.
        row_path : list of (str, str) tuples
            The (column, value) pairs leading to the given row.
        col_path : list of (str, str) tuples
            The (column, value) pairs leading to the given column.
        """
        aggregate, row_path, col_path = self._get_aggregate_paths(row, col)
        agg_column, agg_func = aggregate
        agg_func = getattr(agg_func, '__name__', agg_func)
        row_path = [(col, unicode(value)) for col, value in izip(self.row_pivots, row_path)]
        col_path = [(col, unicode(value)) for col, value in izip(self.col_pivots, col_path)]
        return agg_column, agg_func, row_path, col_path

    def format_value(self, x):
        """ Format a data item as text.
        """
        if math.isnan(x):
            return u''
        elif isinstance(x, float):
            try:
                n = int(x)
            except OverflowError:
                # Infinities don't like to be converted to integers.
                return unicode(x)
            if x == n:
                # Integer.
                return unicode(n)
            else:
                return u'{0:.2f}'.format(x)
        else:
            return unicode(x)

    def get_formatted_block(self, block, headers=True):
        """ Get a list of lists of unicode strings representing the given block
        of cells.

        Parameters
        ----------
        block : (top, left, width, height)
            The indices and extents of the block of cells to format.
        headers : bool, optional
            Add the headers.

        Returns
        -------
        formatted_block : rectangular list of lists of unicode
            The formatted block.
        """
        top, left, width, height = block
        formatted = np.empty((height, width), dtype=object)
        formatted.fill(u'')
        for i in range(height):
            for j in range(width):
                x = self.data(top + i, left + j)
                formatted[i, j] = self.format_value(x)
        if headers:
            top_header, left_header = self._get_csv_headers(block)
            value_block = formatted
            new_shape = (height + top_header.shape[0],
                width + left_header.shape[1])
            formatted = np.empty(new_shape, dtype=object)
            formatted.fill(u'')
            formatted[top_header.shape[0]:, :left_header.shape[1]] = left_header
            formatted[:top_header.shape[0], left_header.shape[1]:] = top_header
            formatted[top_header.shape[0]:, left_header.shape[1]:] = value_block
            # Fill in the pivot names.
            for j, name in enumerate(self.row_pivots):
                name = name
                formatted[top_header.shape[0]-1, j] = name
            for i, name in enumerate(self.col_pivots):
                name = name
                formatted[i, left_header.shape[1]-1] = name

        formatted_block = formatted.tolist()
        return formatted_block

    def format_csv(self, block, headers=True):
        """ Format a block of values as UTF-8 CSV.

        Parameters
        ----------
        block : (top, left, width, height)
            The indices and extents of the block of cells to format.
        headers : bool, optional
            Add the headers.

        Returns
        -------
        csv_text : str (not unicode)
            UTF-8-encoded CSV text.
        """
        formatted_block = self.get_formatted_block(block, headers=headers)
        rows = [[x.encode('utf-8') for x in row] for row in formatted_block]

        f = StringIO()
        w = csv.writer(f)
        w.writerows(rows)
        csv_text = f.getvalue()
        return csv_text

    def sort_header(self, header, aggregate, sort_path, ascending):
        """ Sort one Header by a sort path from the other Header.

        Parameters
        ----------
        header : Header
            The header to sort. I.e. the row_header if we are sorting
            *along* a column and vice versa.
        aggregate : tuple
            The aggregate to sort on.
        sort_path : tuple
            The Node path for the column/row to sort.
        ascending : bool
            Whether the the sort is ascending or descending.
        """
        key = self._get_sort_key(header, aggregate, sort_path, ascending)
        header.sort_by_key(key)

    def unsort_header(self, header):
        """ Restore the sorting of the given Header.
        """
        key = self._get_normal_sort_key(header)
        header.sort_by_key(key)

    def _get_value_by_paths(self, aggregate, row_path, col_path):
        """ Get the value for a cell from a pandas pivot table by its
        path.
        """
        pt = self._get_pivot_table(aggregate, len(row_path), len(col_path))

        if row_path == ():
            # Margin tables use the name of the data frame column.
            row_path = aggregate[0]
        elif len(row_path) == 1:
            # It is a pandas Index, not a MultiIndex, so pull the value
            # out of the tuple.
            row_path = row_path[0]

        if col_path == ():
            # Margin tables use the name of the data frame column.
            col_path = aggregate[0]
        elif len(col_path) == 1:
            # It is a pandas Index, not a MultiIndex, so pull the value
            # out of the tuple.
            col_path = col_path[0]

        try:
            value = pt.get_value(row_path, col_path)
        except KeyError:
            value = np.nan
        return value

    def _get_normal_sort_key(self, header):
        """ Get the normal sort-by-label key function for the given header.
        """
        if header is self.row_header:
            margin_after = self.row_margins == 'after'
        else:
            margin_after = self.col_margins == 'after'

        def key(node):
            # First, make sure that MarginNodes go first or last as
            # configured using boolean XOR and relying on
            # False < True.
            #
            # Margin   after   Result
            # False    False   True
            # True     False   False
            # False    True    False
            # True     True    True
            margin_key = not (isinstance(node, MarginNode) ^ margin_after)
            if isinstance(node, AggregationNode):
                # Sort AggregationNodes by their position in the
                # configured list of aggregates. They should only show
                # up in comparisons with other AggregationNodes.
                value_key = self.aggregates.index(node.value)
            else:
                value_key = node.value
            return (margin_key, value_key)

        return key

    def _get_sort_key(self, header, aggregate, sort_path, ascending):
        """ Get the sort key for a leaf that is being sorted.
        """
        if header is self.row_header:
            margin_after = self.row_margins == 'after'
            def data(node):
                return self._get_value_by_paths(aggregate, node.path,
                    sort_path)
        else:
            margin_after = self.col_margins == 'after'
            def data(node):
                return self._get_value_by_paths(aggregate, sort_path,
                    node.path)

        def key(node):
            margin_key = not (isinstance(node, MarginNode) ^ margin_after)
            if isinstance(node, AggregationNode):
                value_key = self.aggregates.index(node.value)
                blank = False
            else:
                value_key = data(node)
                blank = (value_key is None or math.isnan(value_key))
                # FIXME: we must assume that the value is a numeric type
                # that can be negated for this sort key to work.
                if not ascending and not blank:
                    value_key = -value_key
            # Margins go first or last, as configured.
            # Blank cells go later than non-blank cells, regardless of
            # sort order.
            # Then we look at the value.
            return (margin_key, blank, value_key)

        return key

    def _get_pivot_table(self, aggregate, row_depth, col_depth):
        """ Return a (cached) pivot table for the requested depths.
        """
        column, aggfunc = aggregate
        # If we are given a string that needs to be turned into
        # a function, or renamed, do it here.
        aggfunc = agg_funcs.get(aggfunc, aggfunc)
        key = (aggregate, row_depth, col_depth)
        if key not in self._pivot_tables:
            if row_depth == col_depth == 0:
                # Grand margin.
                margin = self.filtered_frame[column].groupby(lambda x: 0).agg(aggfunc)[0]
                # Make a full DataFrame indexed by the aggregated column
                # name on both axes in order to match how the other
                # margin tables are accessed.
                table = pandas.DataFrame([[margin]],
                    index=pandas.Index([column], dtype=object),
                    columns=pandas.Index([column], dtype=object),
                )
                self._pivot_tables[key] = table
            elif col_depth == 0:
                # We are computing a margin table for a whole aggregation,
                # grouped by the rows.
                rows = list(self.row_pivots[:row_depth])
                margins = self.filtered_frame[rows + [column]].groupby(rows).agg(aggfunc)
                self._pivot_tables[key] = margins
            elif row_depth == 0:
                # We are computing a margin table for a whole aggregation,
                # grouped by the columns.
                cols = list(self.col_pivots[:col_depth])
                margins = self.filtered_frame[cols + [column]].groupby(cols).agg(aggfunc)
                # Transpose so the columns can be accessed as columns.
                self._pivot_tables[key] = margins.T
            else:
                pt = self.filtered_frame.pivot_table(
                    values=column,
                    rows=self.row_pivots[:row_depth],
                    cols=self.col_pivots[:col_depth], 
                    aggfunc=aggfunc,
                )
                if isinstance(pt, pandas.DataFrame):
                    # Drop extraneous columns.
                    pt = pt.dropna(axis=1, how='all')
                self._pivot_tables[key] = pt
        return self._pivot_tables[key]

    @on_trait_change('row_header:update,col_header:update')
    def _fire_header_update(self, object, name, old, new):
        self.ensure_cache(object, new)

    def ensure_cache(self, header, event):
        """ Ensure that the cache is full given the changes from the
        HeaderEvent, then send an event notifying the change.

        The can be overridden to be asynchronous if necessary.
        """
        if header is self.row_header:
            row_leaves = event.new_leaves
            col_leaves = self.col_header.leaves
        else:
            row_leaves = self.row_header.leaves
            col_leaves = event.new_leaves

        row_depths = set(leaf.depth for leaf in row_leaves)
        col_depths = set(leaf.depth for leaf in col_leaves)
        for aggregate in self.aggregates:
            for col_depth, row_depth in product(col_depths, row_depths):
                self._get_pivot_table(aggregate, row_depth, col_depth)

        self.send_update(header, event)

    def _get_aggregate_paths(self, row, col):
        """ Get the aggregate and the row/col paths for the given
        row,col indices.
        """
        row_leaf = self.row_header.leaves[row]
        col_leaf = self.col_header.leaves[col]
        # FIXME: This is slightly excessive checking. If we need to
        # optimize, then we can test for the presence of the .aggregates
        # list on each Header and cache that test. But for now, asserts
        # are good for testing.
        if isinstance(col_leaf, AggregationNode):
            assert not isinstance(row_leaf, AggregationNode)
            aggregate = col_leaf.value
        elif isinstance(row_leaf, AggregationNode):
            aggregate = row_leaf.value
        else:
            raise ValueError("One of the rows or the column leaves needs to be an AggregationNode.")
        return aggregate, row_leaf.path, col_leaf.path

    def _get_csv_headers(self, block):
        """ Return the left and top headers for a selected block.

        Parameters
        ----------
        block : (top, left, width, height)
            The indices and extents of the block of cells to format.

        Returns
        -------
        top_header : object ndarray of str, (col_depth, width)
        left_header : object ndarray of str, (height, row_depth)
            The headers.
        """
        top, left, width, height = block
        top_header = self._get_axis_csv_header(self.col_header, left,
            left+width)
        top_header = top_header.transpose()
        left_header = self._get_axis_csv_header(self.row_header, top,
            top+height)
        return top_header, left_header

    def _get_axis_csv_header(self, header, start, stop):
        """ Get one axis header for the CSV labels.
        """
        depth = max(header.depths) + (header.aggregates != [])
        paths = []
        for leaf in header.leaves[start:stop]:
            path = [u''] * depth
            node_path = leaf.ancestors()
            if isinstance(leaf, AggregationNode):
                # Always last.
                path[-1] = format_aggregate(leaf.value)
            else:
                node_path.append(leaf)
            for i, node in enumerate(node_path):
                path[i] = node.text
            path = [x.encode('utf-8') for x in path]
            paths.append(path)
        # We might transpose this later depending on the axis.
        csv_header = np.array(paths, dtype=object)
        # Remove trailing duplicates in each column.
        for j in range(csv_header.shape[1]):
            for i in range(csv_header.shape[0]-1, 0, -1):
                if csv_header[i,j] == csv_header[i-1,j]:
                    csv_header[i,j] = u''
        return csv_header

    def send_update(self, header, event):
        """ Forward a structure update event.
        """
        if header is self.row_header:
            header_name = 'rows'
        elif header is self.col_header:
            header_name = 'cols'
        else:
            raise ValueError("Expected one of row_header or col_header. Got {0!r} ({1!r})".format(header, type(header)))
        self.update = (header_name, event)

    def set_pivots(self, row_pivots, col_pivots):
        """ Set new pivot lists in tandem.

        """
        self.trait_set(
            row_pivots=row_pivots,
            col_pivots=col_pivots,
        )
        self._fire_filtered_frame(self.filtered_frame)

    @on_trait_change('filtered_frame')
    def _fire_filtered_frame(self, new):
        # Clear the cache.
        self._pivot_tables.clear()
        self.reset_headers()
        self.update = ('all', new)

    @on_trait_change('frame')
    def _new_frame(self):
        for name, value_or_expr in self.extra_columns:
            self.add_column(name, value_or_expr)
        self.refilter()

    def _row_current_sort_changed(self, new):
        if new is None:
            self.unsort_header(self.row_header)
        else:
            self.sort_header(self.row_header, *new)

    def _col_current_sort_changed(self, new):
        if new is None:
            self.unsort_header(self.col_header)
        else:
            self.sort_header(self.col_header, *new)

