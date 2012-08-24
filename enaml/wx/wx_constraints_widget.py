#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from casuarius import ConstraintVariable 

from .wx_widget_component import WxWidgetComponent


class LayoutBox(object):
    """ A class which encapsulates a layout box using casuarius 
    constraint variables.

    The constraint variables are created on an as-needed basis, this
    allows Enaml widgets to define new constraints and build layouts
    with them, without having to specifically update this client 
    code.

    """
    def __init__(self, name, owner):
        """ Initialize a LayoutBox.

        Parameters
        ----------
        name : str
            A name to use in the label for the constraint variables in
            this layout box.

        owner : str
            The owner id to use in the label for the constraint variables
            in this layout box.

        """
        self._name = name
        self._owner = owner
        self._primitives = {}

    def primitive(self, name, force_create=True):
        """ Returns a primitive casuarius constraint variable for the
        given name.

        Parameters
        ----------
        name : str
            The name of the constraint variable to return.

        force_create : bool, optional
            If the constraint variable does not yet exist and this 
            parameter is True, then the constraint variable will be
            created on-the-fly. If the parameter is False, and the
            variable does not exist, a ValueError will be raised.

        """
        primitives = self._primitives
        try:
            res = primitives[name]
        except KeyError:
            if force_create:
                label = '{0}_{1}'.format(self._name, self._owner)
                res = primitives[name] = ConstraintVariable(label)
            else:
                msg = 'Constraint variable `{0}` does not exist'
                raise ValueError(msg.format(name))
        return res


class WxConstraintsWidget(WxWidgetComponent):
    """ A Wx implementation of an Enaml ConstraintsWidget.

    """
    #: The list of hard constraints which must be applied to the widget.
    #: These constraints are computed lazily and only once since they
    #: are assumed to never change.
    _hard_constraints = []

    #--------------------------------------------------------------------------
    # Setup Methods
    #--------------------------------------------------------------------------
    def create(self, tree):
        """ Create and initialize the control.

        """
        super(WxConstraintsWidget, self).create(tree)
        layout = tree['layout']
        self.hug = layout['hug']
        self.resist_clip = layout['resist_clip']
        self.constraints = layout['constraints']
        self.layout_box = LayoutBox(type(self).__name__, self.widget_id())
        
    #--------------------------------------------------------------------------
    # Message Handlers
    #--------------------------------------------------------------------------
    def on_action_relayout(self, content):
        """ Handle the 'relayout' action from the Enaml widget.

        """
        # XXX these variables should really be made private. And the
        # WxContainer needs to get in on the action to grab the 
        # share_layout flag.
        self.hug = content['hug']
        self.resist_clip = content['resist_clip']
        self.constraints = content['constraints']
        self.relayout()

    #--------------------------------------------------------------------------
    # Layout Handling
    #--------------------------------------------------------------------------
    def relayout(self):
        """ Peform a relayout for this constraints widget.

        The default behavior of this method is to proxy the call up the
        tree of ancestors until it is either handled by a subclass which
        has reimplemented this method (see WxContainer), or the ancestor
        is not an instance of WxConstraintsWidget, at which point the
        layout request is dropped.

        """
        parent = self.parent()
        if isinstance(parent, WxConstraintsWidget):
            parent.relayout()

    def size_hint_constraints(self):
        """ Creates the list of size hint constraints for this widget.

        This method using the provided size hint of the widget and the
        policies for 'hug' and 'resist_clip' to generate casuarius 
        LinearConstraint objects which respect the size hinting of the
        widget.

        If the size hint of the underlying widget is not valid, then
        no constraints will be generated.

        Returns
        -------
        result : list
            A list of casuarius LinearConstraint instances.

        """
        cns = []
        push = cns.append
        hint = self.widget().GetBestSize()
        if hint.IsFullySpecified():
            width_hint = hint.width
            height_hint = hint.height
            primitive = self.layout_box.primitive
            width = primitive('width')
            height = primitive('height')
            hug_width, hug_height = self.hug
            resist_width, resist_height = self.resist_clip
            if width_hint >= 0:
                if hug_width != 'ignore':
                    cn = (width == width_hint) | hug_width
                    push(cn)
                if resist_width != 'ignore':
                    cn = (width >= width_hint) | resist_width
                    push(cn)
            if height_hint >= 0:
                if hug_height != 'ignore':
                    cn = (height == height_hint) | hug_height
                    push(cn)
                if resist_height != 'ignore':
                    cn = (height >= height_hint) | resist_height
                    push(cn)
        return cns

    def hard_constraints(self):
        """ Generate the constraints which must always be applied.

        These constraints are generated once the first time this method
        is called. The results are then cached and returned immediately
        on future calls.

        Returns
        -------
        result : list
            A list of casuarius LinearConstraint instance.

        """
        cns = self._hard_constraints
        if not cns: 
            primitive = self.layout_box.primitive
            left = primitive('left')
            top = primitive('top')
            width = primitive('width')
            height = primitive('height')
            cns = [left >= 0, top >= 0, width >= 0, height >= 0]
            self._hard_constraints = cns
        return cns

    def geometry_updater(self):
        """ A method which can be called to create a function which
        will update the layout geometry of the underlying widget.

        The parameter and return values below describe the function
        that is returned by calling this method.

        Parameters
        ----------
        dx : float
            The offset of the parent widget from the computed origin
            of the layout. This amount is subtracted from the computed 
            layout 'x' amount, which is expressed in the coordinates
            of the owner widget.

        dy : float
            The offset of the parent widget from the computed origin
            of the layout. This amount is subtracted from the computed 
            layout 'y' amount, which is expressed in the coordinates
            of the layout owner widget.

        Returns
        -------
        result : (x, y)
            The computed layout 'x' and 'y' amount, expressed in the
            coordinates of the layout owner widget.

        """
        # The return function is a hyper optimized (for Python) closure
        # that will is called on every resize to update the geometry of
        # the widget. This is explicitly not idiomatic Python code. It 
        # exists purely for the sake of efficiency and was justified 
        # with profiling.
        primitive = self.layout_box.primitive
        x = primitive('left')
        y = primitive('top')
        width = primitive('width')
        height = primitive('height')
        setdims = self.widget().SetDimensions
        def update_geometry(dx, dy):
            nx = x.value
            ny = y.value
            setdims(nx - dx, ny - dy, width.value, height.value)
            return nx, ny
        # Store a reference to self on the updater, so that the layout
        # container can know the object on which the updater operates.
        update_geometry.item = self
        return update_geometry

