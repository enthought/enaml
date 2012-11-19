#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Instance, Tuple
from enable.component import Component
from enable.kiva_graphics_context import GraphicsContext

from ..widgets.constraints_widget import ConstraintsWidget
from ..noncomponents.image import ImageFromArray


class CanvasGraphicsContext(GraphicsContext):

    def render_component(self, component, container_coords=False):
        """ Renders the given component.

        Parameters
        ----------
        component : Component
            The component to be rendered.
        container_coords : Boolean
            Whether to use coordinates of the component's container

        Description
        -----------
        If *container_coords* is False, then the (0,0) coordinate of this
        graphics context corresponds to the lower-left corner of the
        component's **outer_bounds**. If *container_coords* is True, then the
        method draws the component as it appears inside its container, i.e., it
        treats (0,0) of the graphics context as the lower-left corner of the
        container's outer bounds.
        """

        x, y = component.outer_position
        if not container_coords:
            x = -x
            y = -y
        with self:
            self.translate_ctm(x, y)
            component.draw(self, view_bounds=(0, 0, self.width(), self.height()))
        return        

class RemoteCanvas(ConstraintsWidget):
    """ An extremely simple widget for displaying an enable canvas
    
    """
    #: The enable component
    component = Instance(Component)
    
    #: How strongly a component hugs it's contents' width. Enable components
    #: ignore the width hug by default, so they expand freely in width.
    hug_width = 'ignore'
    
    #: How strongly a component hugs it's contents' height. Enable components
    #: ignore the height hug by default, so they expand freely in height.
    hug_height = 'ignore'

    _render_size = Tuple(0,0)
    _img_buffer = Instance(CanvasGraphicsContext)

    #--------------------------------------------------------------------------
    # Initialization
    #--------------------------------------------------------------------------
    def bind(self):
        """ Bind the change handlers for the control

        """
        super(RemoteCanvas, self).bind()
        self.on_trait_change(self._regenerate_buffer, '_render_size')

    #--------------------------------------------------------------------------
    # Message Handling
    #--------------------------------------------------------------------------
    def on_action_size_changed(self, content):
        """ Handle the 'size_changed' action from the client widget.

        """
        size = content['size']
        self.set_guarded(_render_size=size)

    def _regenerate_buffer(self):
        """ Rebuild the backing store used to render the enable component
            with the new render size

        """
        w, h = self._render_size
        
        rem = w % 4
        # Each scanline needs to be 32bit aligned (for Qt)
        if rem: w += (4 - rem)
        
        self._img_buffer = CanvasGraphicsContext((w,h))
        self._render()

    def _render(self):
        """ Render the enable component into the backbuffer and send to the client

        """
        render_size = self._render_size
        component = self.component
        component.outer_bounds = render_size
        component.do_layout(force=True)
        
        context = self._img_buffer
        context.clear()
        context.render_component(component)
        
        data = context.bmp_array
        canvas = ImageFromArray(data,
                                render_size,
                                'bgra32')
        content = {'canvas': canvas,
                   'stride': data.strides[0]}
        self.send_action('set_canvas', content)
