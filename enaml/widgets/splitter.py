#------------------------------------------------------------------------------
# Copyright (c) 2011, Enthought, Inc.
# All rights reserved.
#------------------------------------------------------------------------------
from abc import abstractmethod
from itertools import izip_longest

from traits.api import Bool, List, Either, Int

from .container import Container
from .layout_component import LayoutComponent, AbstractTkLayoutComponent
from .layout_task_handler import LayoutTaskHandler

from ..enums import Orientation


class AbstractTkSplitter(AbstractTkLayoutComponent):
    """ The abstract toolkit Splitter interface.

    A toolkit splitter container is responsible for handling changes on 
    a shell Splitter and proxying those changes to and from its internal 
    toolkit widget.

    """
    @abstractmethod
    def set_splitter_sizes(self, sizes):
        """ Set the splitter sizes for the children.

        """
        raise NotImplementedError

    @abstractmethod
    def shell_orientation_changed(self, orientation):
        """ The change handler for the 'orientation' attribute of the 
        shell object.

        """
        raise NotImplementedError

    @abstractmethod
    def shell_live_drag_changed(self, live_drag):
        """ The change handler for the 'live_drag' attribute of the
        shell object.

        """
        raise NotImplementedError
        
    @abstractmethod
    def shell_layout_children_changed(self, children):
        """ The change handler for the 'layout_children' attribute of 
        the shell object.

        """
        raise NotImplementedError


class Splitter(LayoutTaskHandler, LayoutComponent):
    """ A LayoutComponent subclass that displays its children in separate
    resizable compartements that are connected with a resizing bar.
     
    """
    #: The orientation of the Splitter. 'horizontal' means the children 
    #: are laid out left to right, 'vertical' means top to bottom.
    orientation = Orientation('horizontal')

    #: Whether the child widgets resize as a splitter is being dragged
    #: (True), or if a simple indicator is drawn until the drag handle
    #: is released (False). The default is True.
    live_drag = Bool(True)
    
    #: A list of preferred sizes for each compartment of the splitter, or None
    #: if there is no preference for the size.
    preferred_sizes = List(Either(None, Int, default=None))
    
    #: How strongly a component hugs it's contents' width. A Splitter
    #: container ignores its width hug by default, so it expands freely
    #: in width.
    hug_width = 'ignore'

    #: How strongly a component hugs it's contents' height. A Splitter
    #: container ignores its height hug by default, so it expands freely
    #: in height.
    hug_height = 'ignore'

    #--------------------------------------------------------------------------
    # Change Handlers
    #--------------------------------------------------------------------------
    def _orientation_changed(self):
        """ The change handler for the 'orientation' attribute. 
        This simply requests a relayout.

        """
        self.request_relayout()

    def _on_layout_deps_changed(self):
        """ A change handler for triggering a relayout when any of the
        layout dependencies change. It simply requests a relayout.

        """
        self.request_relayout()

    #--------------------------------------------------------------------------
    # Setup Methods
    #--------------------------------------------------------------------------
    def _setup_finalize(self):
        """ Overridden setup method to initialize the sizes of the 
        splitter.

        """
        super(Splitter, self)._setup_finalize()
        self.update_splitter_sizes()

    #--------------------------------------------------------------------------
    # Overrides
    #--------------------------------------------------------------------------
    def initialize_layout(self):
        """ A reimplemented parent class method which hooks up change
        handlers for child attributes which will cause a change in 
        the layout.

        """
        self.on_trait_change(
            self._on_layout_deps_changed, (
                'layout_children:visible, '
                'layout_children:size_hint_updated, '
            )
        )

    def do_relayout(self):
        """ A reimplemented LayoutTaskHandler handler method which will
        perform necessary update activity when a relayout it requested.

        """
        # This method is called whenever a relayout is requested.
        # We update the size of the splitter components and fire 
        # off a size hint updated event so that any parents can
        # react to our potential new size.
        self.update_splitter_sizes()
        self.size_hint_updated()

    #--------------------------------------------------------------------------
    # Update Methods
    #--------------------------------------------------------------------------
    def update_splitter_sizes(self):
        """ Update the sizes of each of the splitters based on the size
        hints of the children and the orientation of the splitter. The
        minimum sizes of the children are also computed and applied.

        """
        # TODO - the setting of the min sizes here could be cleaner
        num_children = len(self.layout_children)
        sizes = []
        i = ['horizontal', 'vertical'].index(self.orientation)
        for child, size in izip_longest(self.layout_children, self.preferred_sizes[:num_children]):
            if size is None:
                if isinstance(child, Container):
                    min_size = child.compute_min_size()
                    child.set_min_size(*min_size)
                hint = child.size_hint()[i]
                if hint <= 0:
                    hint = child.min_size()[i]
                sizes.append(hint)
            else:
                sizes.append(size)
        self.abstract_obj.set_splitter_sizes(sizes)
    
