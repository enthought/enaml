#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------

from traits.api import Instance, Str, on_trait_change

from .layout.layout_helpers import (DEFAULT_SPACE, _space_, align_v_center,
    horizontal, vertical)
from .layout.symbolics import ConstraintVariable
from .container import AbstractTkContainer, Container


class AbstractTkForm(AbstractTkContainer):
    """ The abstract toolkit Form interface.

    """


class Form(Container):
    """ A Container subclass that provides for laying out child Components as
    a two-column form.

    On the left are the typically Labels. On the right are the actual widgets
    for data entry. The children should be in alternating label/widget order.

    """

    #: The ConstraintVariable giving the midline along which the labels and
    #: widgets are aligned.
    midline = Instance(ConstraintVariable, args=('midline',))

    #: The strength for the form layout constraints.
    # FIXME: Use an Enum.
    layout_strength = Str('strong')

    def _default_constraints_default(self):
        return self._compute_form_constraints_for_children()

    @on_trait_change('children,children_items')
    def _update_default_constraints(self):
        self._needs_update_constraints = True

    def update_constraints(self):
        """ Update the constraints for this component.

        """
        self.default_constraints = self._compute_form_constraints_for_children()
        super(Form, self).update_constraints()

    def _compute_form_constraints_for_children(self):
        """ Compute the current form constraints for the current children.

        """
        labels = self.children[::2]
        widgets = self.children[1::2]
        if len(labels) != len(widgets):
            # FIXME: Ignore the mismatched final label if the number of children
            # is odd. Qt lays out a final odd child as taking up the whole
            # horizontal space at the bottom.
            nrows = min(len(labels), len(widgets))
            labels = labels[:nrows]
            widgets = widgets[:nrows]
        label_args = [self.top] + labels + [self.bottom]
        widget_args = [self.top] + widgets + [self.bottom]
        constraints = [
            vertical(*label_args) | self.layout_strength,
            vertical(*widget_args) | self.layout_strength,
        ]
        for widget in widgets:
            constraints.append((widget.left == self.midline) | self.layout_strength)
        for label, widget in zip(labels, widgets):
            constraints.extend([
                # FIXME: pick a better margin.
                horizontal(self.left, label, widget, self.right) | self.layout_strength,
                # FIXME: baselines would be much better.
                align_v_center(label, widget) | self.layout_strength,
            ])
        return constraints
