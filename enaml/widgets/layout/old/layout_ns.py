from abc import ABCMeta, abstractmethod

from ..base_component import BaseComponent
from .symbolics import MultiConstraint


# Singleton LayoutNS object.
_layout_ns = None

# Map orientations to dictionaries mapping abstract, orientation-independent
# names for variables to their orientation-specific names.
VARIABLE_MAP = dict(
    horizontal=dict(
        first='left',
        last='right',
        extent='width',
        center='h_center',
    ),
    vertical=dict(
        first='top',
        last='bottom',
        extent='height',
        center='v_center',
    ),
)

class Spacer(object):
    """ The default space between objects.

    """

    def __init__(self, extent=8, springy=False):
        self.extent = extent
        self.springy = springy

    def relationship(self, first, second, orientation):
        if self.springy:
            rel = Expando(first, second, orientation)
        else:
            rel = SpaceBetween(first, second, orientation)
        rel.extent = self.extent
        return rel

    def __call__(self, extent):
        return Spacer(extent=extent, springy=self.springy)


class Border(object):
    """ A border of the parent.

    """

    #: The parent component.
    parent = None


class Relationship(object):
    """ The relationship held by two components.

    """

    __metaclass__ = ABCMeta

    def __init__(self, first, second, orientation):
        self.first = first
        self.second = second
        self.orientation = orientation
        self.variables = VARIABLE_MAP[orientation]

    def get_first_variable(self):
        """ Get the relevant ConstraintVariable for the first item.

        """
        if self.first is None:
            raise ValueError('.first is None')
        if isinstance(self.first, Border):
            return getattr(self.first.parent, self.variables['first'])
        elif isinstance(self.first, BaseComponent):
            return getattr(self.first, self.variables['last'])
        else:
            raise TypeError('Expected a Border or a Component. Got a %r.' % type(self.first))

    def get_second_variable(self):
        """ Get the relevant ConstraintVariable for the first item.

        """
        if self.second is None:
            raise ValueError('.second is None')
        if isinstance(self.second, Border):
            return getattr(self.second.parent, self.variables['last'])
        elif isinstance(self.second, BaseComponent):
            return getattr(self.second, self.variables['first'])
        else:
            raise TypeError('Expected a Border or a Component. Got a %r.' % type(self.second))

    @abstractmethod
    def constraint(self, strength='required'):
        """ Return the constraint represented by this relationship.

        """
        raise NotImplementedError


class Abut(Relationship):
    """ Two objects abut each other.

    """

    def constraint(self, strength='required'):
        v1 = self.get_first_variable()
        v2 = self.get_second_variable()
        return (v1 == v2) | strength


class SpaceBetween(Relationship):
    """ Two objects have some space between them.

    """

    extent = 0

    def constraint(self, strength='required'):
        v1 = self.get_first_variable()
        v2 = self.get_second_variable()
        return (v2 == v1 + self.extent) | strength


class Expando(Relationship):
    """ Two objects have an expandable space between them.

    """

    extent = 0

    def constraint(self, strength='required'):
        v1 = self.get_first_variable()
        v2 = self.get_second_variable()
        return (v2 >= v1 + self.extent) | strength


class LayoutNS(object):
    """ Namespace for layout-related tools to make available inside Enaml files.

    """

    def __new__(cls):
        global _layout_ns
        if _layout_ns is None:
            _layout_ns = object.__new__(cls)
        return _layout_ns

    @property
    def _(self):
        """ A default spacer.

        """
        return Spacer()

    @property
    def I(self):
        """ One of the borders of the parent.

        """
        return Border()

    def spring(self, min_extent=8):
        return Spacer(min_extent, springy=True)

    def linear_layout(self, orientation, *components, **kwds):
        """ Lay out Components in a line.

        """
        if len(components) == 0:
            return MultiConstraint()
        real_components = self._extract_real_components(components)

        if isinstance(components[0], Border):
            border = components[0]
            # Get the parent of the first real component. This will be what the
            # border is attached to.
            border.parent = real_components[0].parent

        if isinstance(components[-1], Border):
            border = components[-1]
            # Get the parent of the last real component. This will be what the
            # border is attached to.
            border.parent = real_components[-1].parent

        default_strength = kwds.get('strength', 'required')

        constraints = []
        items = []
        relationship = Abut
        for item in components:
            if isinstance(item, basestring):
                last_constraint = constraints.pop()
                last_constraint = last_constraint | item
                constraints.append(last_constraint)
            elif isinstance(item, Spacer):
                relationship = item.relationship
            else:
                items.append(item)
                # Only keep the last two items.
                items = items[-2:]
                if len(items) == 2:
                    rel = relationship(items[0], items[1], orientation)
                    constraints.append(rel.constraint(default_strength))
                    # Reset the relationship.
                    relationship = Abut
        return MultiConstraint(constraints)

    def H(self, *components, **kwds):
        """ Lay out components horizontally.

        """
        mc = self.linear_layout('horizontal', *components, **kwds)
        return mc

    def V(self, *components, **kwds):
        """ Lay out components vertically.

        """
        mc = self.linear_layout('vertical', *components, **kwds)
        return mc

    def size_hint(self, component):
        """ Provide constraints for the size hints.

        """
        w, h = component.size_hint()
        return MultiConstraint([
            (component.width == w),
            (component.height == h),
        ])

    def align(self, var, *components):
        """ Align the specified variables for the given components.

        """
        c0 = components[0]
        return MultiConstraint([
            getattr(c0, var) == getattr(c, var)
            for c in components[1:]
        ])

    def _extract_real_components(self, objects):
        """ Extract real Components from a list of objects and maintain their
        relative order.

        """
        # Use BaseComponent to avoid circular imports.
        return [x for x in objects if isinstance(x, BaseComponent)]

