#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Instance, Str

from casuarius import ConstraintVariable

from .layout.layout_helpers import align_v_center, horizontal, vertical
from .container import AbstractTkContainer, Container


class AbstractTkForm(AbstractTkContainer):
    """ The abstract toolkit Form interface.

    """
    pass


class Form(Container):
    """ A Container subclass that arranges child Components as a two
    column form.

    The left column is typically Labels (but this is not a requirement).
    The right are the actual widgets for data entry. The children should
    be in alternating label/widget order. If there are an odd number
    of children, the last child will span both columns.

    """
    #: The ConstraintVariable giving the midline along which the labels
    #: and widgets are aligned.
    midline = Instance(ConstraintVariable)
    def _midline_default(self):
        label = 'midline_{0}_{1:x}'.format(type(self).__name__, id(self))
        return ConstraintVariable(label)

    #: The strength for the form layout constraints.
    # FIXME: Use an Enum.
    layout_strength = Str('strong')

    def default_user_constraints(self):
        """ Overridden parent class method which returns an empty list.
        All constraints are supplied by 'container_constraints()'.

        """
        return []

    def container_constraints(self):
        """ Computes the current form constraints for the current
        children.

        """
        # FIXME: do something sensible when children are not visible.
        children = self.children
        labels = children[::2]
        widgets = children[1::2]

        n_labels = len(labels)
        n_widgets = len(widgets)

        if n_labels != n_widgets:
            if n_labels > n_widgets:
                odd_child = labels.pop()
            else:
                odd_child = widgets.pop()
        else:
            odd_child = None

        layout_strength = self.layout_strength
        constraints = []

        # Align the left side of each widget with the midline constraint
        # variable of the form.
        midline = self.midline
        for widget in widgets:
            cn = (widget.left == midline) | layout_strength
            constraints.append(cn)

        # Arrange each label/widget pair horizontally in the form
        left = self.left
        right = self.right
        for label, widget in zip(labels, widgets):
            constraints.extend([
                # FIXME: pick a better margin.
                horizontal(left, label, widget, right) | layout_strength,
                # FIXME: baselines would be much better.
                align_v_center(label, widget) | layout_strength,
            ])

        # Arrange the widgets vertically in the form
        if odd_child is not None:
            widget_args = [self.top] + widgets + [odd_child, self.bottom]
            constraints.append(vertical(*widget_args) | layout_strength)
        else:
            widget_args = [self.top] + widgets + [self.bottom]
            constraints.append(vertical(*widget_args) | layout_strength)

        # Finally, handle the horizontal constraints of the odd child.
        if odd_child is not None:
            cn = horizontal(left, odd_child, right) | layout_strength
            constraints.append(cn)

        return constraints

