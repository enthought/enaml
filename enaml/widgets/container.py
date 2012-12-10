#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Property, Instance, Bool, cached_property

from enaml.core.trait_types import CoercingInstance
from enaml.layout.box_model import ContentsBoxModel
from enaml.layout.geometry import Box
from enaml.layout.layout_helpers import vbox

from .constraints_widget import ConstraintsWidget, get_from_box_model


class Container(ConstraintsWidget):
    """ A ConstraintsWidget subclass that provides functionality for
    laying out constrainable children according to their system of
    constraints.

    The Container is the canonical component used to arrange child
    widgets using constraints-based layout. Given a heierarchy of
    components, the top-most Container will be charged with the actual
    layout of the decendents. This allows constraints to cross the
    boundaries of Containers, enabling powerful and flexible layouts.

    There are widgets whose boundaries constraints may not cross. Some
    examples of these would be a ScrollArea or a TabGroup. See the
    documentation of a given container component as to whether or not
    constraints may cross its boundaries.

    """
    #: A boolean which indicates whether or not to allow the layout
    #: ownership of this container to be transferred to an ancestor.
    #: This is False by default, which means that every container
    #: get its own layout solver. This improves speed and reduces
    #: memory use (by keeping a solver's internal tableaux small)
    #: but at the cost of not being able to share constraints
    #: across Container boundaries. This flag must be explicitly
    #: marked as True to enable sharing.
    share_layout = Bool(False)

    #: A read-only symbolic object that represents the internal left
    #: boundary of the content area of the container.
    contents_left = Property(fget=get_from_box_model)

    #: A read-only symbolic object that represents the internal right
    #: boundary of the content area of the container.
    contents_right = Property(fget=get_from_box_model)

    #: A read-only symbolic object that represents the internal top
    #: boundary of the content area of the container.
    contents_top = Property(fget=get_from_box_model)

    #: A read-only symbolic object that represents the internal bottom
    #: boundary of the content area of the container.
    contents_bottom = Property(fget=get_from_box_model)

    #: A read-only symbolic object that represents the internal width of
    #: the content area of the container.
    contents_width = Property(fget=get_from_box_model)

    #: A read-only symbolic object that represents the internal height of
    #: the content area of the container.
    contents_height = Property(fget=get_from_box_model)

    #: A read-only symbolic object that represents the internal center
    #: along the vertical direction the content area of the container.
    contents_v_center = Property(fget=get_from_box_model)

    #: A read-only symbolic object that represents the internal center
    #: along the horizontal direction of the content area of the container.
    contents_h_center = Property(fget=get_from_box_model)

    #: A box object which holds the padding for this component. The
    #: padding is the amount of space between the outer boundary box
    #: and the content box. The default padding is (10, 10, 10, 10).
    #: Certain subclasses, such as GroupBox, may provide additional
    #: margin than what is specified by the padding.
    padding = CoercingInstance(Box, (10, 10, 10, 10))

    #: A read only property which returns this container's widgets.
    widgets = Property(depends_on='children')

    #: Containers freely exapnd in width and height. The size hint
    #: constraints for a Container are used when the container is
    #: not sharing its layout. In these cases, expansion of the
    #: container is typically desired.
    hug_width = 'ignore'
    hug_height = 'ignore'

    #: The private storage the box model instance for this component.
    _box_model = Instance(ContentsBoxModel)
    def __box_model_default(self):
        return ContentsBoxModel(self.object_id)

    #--------------------------------------------------------------------------
    # Initialization
    #--------------------------------------------------------------------------
    def bind(self):
        """ Bind the necessary change handlers for the control.

        """
        super(Container, self).bind()
        self.on_trait_change(self._send_relayout, 'share_layout, padding')

    #--------------------------------------------------------------------------
    # Children Events
    #--------------------------------------------------------------------------
    def children_event(self, event):
        """ Handle a `ChildrenEvent` on a container.

        This event handler will send a relayout event if the `Container`
        is active and the user has not defined their own constraints.

        """
        super(Container, self).children_event(event)
        if self.is_active and not self.constraints:
            self._send_relayout()

    #--------------------------------------------------------------------------
    # Constraints Generation
    #--------------------------------------------------------------------------
    def _layout_info(self):
        """ An overridden parent class method which adds the 'share'
        layout key to the dict of layout information sent to the client.

        """
        layout = super(Container, self)._layout_info()
        layout['share_layout'] = self.share_layout
        layout['padding'] = self.padding
        return layout

    def _default_constraints(self):
        """ Supplies a default vbox constraint to the constraints
        children of the container if other constraints are not given.

        """
        cns = super(Container, self)._default_constraints()
        cns.append(vbox(*self.widgets))
        return cns

    #--------------------------------------------------------------------------
    # Property Getters
    #--------------------------------------------------------------------------
    @cached_property
    def _get_widgets(self):
        """ The getter for the 'widgets' property

        Returns
        -------
        result : tuple
            The tuple of ContraintsWidgets defined as children of this
            Container.

        """
        isinst = isinstance
        widgets = (c for c in self.children if isinst(c, ConstraintsWidget))
        return tuple(widgets)

