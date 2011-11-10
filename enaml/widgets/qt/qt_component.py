#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt import QtGui
from .qt_base_component import QtBaseComponent
from .qt_resizing_widgets import QResizingFrame, QResizingWidget
from .styling import q_color_from_color, q_font_from_font

from ..component import AbstractTkComponent


class QtComponent(QtBaseComponent, AbstractTkComponent):
    """ A Qt4 implementation of Component.

    A QtComponent is not meant to be used directly. It provides some
    common functionality that is useful to all widgets and should
    serve as the base class for all other classes.

    .. note:: This is not a HasTraits class.

    """
    #: The Qt widget created by the component
    widget = None

    #--------------------------------------------------------------------------
    # Setup Methods
    #--------------------------------------------------------------------------
    def create(self):
        self.widget = QResizingFrame(self.parent_widget())
    
    def initialize(self):
        """Initialize the attributes of the Qt widget.
        """
        super(QtComponent, self).initialize()
        
        shell = self.shell_obj
        if shell.bg_color:
            role = self.widget.backgroundRole()
            self.set_role_color(role, shell.bg_color)
        if shell.fg_color:
            role = self.widget.foregroundRole()
            self.set_role_color(role, shell.fg_color)
        if shell.font:
            self.set_font(shell.font)

    def bind(self):
        super(QtComponent, self).bind()

        if isinstance(self.widget, QResizingWidget):
            self.widget.resized.connect(self.on_resize)

    #--------------------------------------------------------------------------
    # Implementation
    #--------------------------------------------------------------------------
    @property
    def toolkit_widget(self):
        """ A property that returns the toolkit specific widget for this
        component.

        """
        return self.widget

    def size(self):
        """ Return the size of the internal toolkit widget as a
        (width, height) tuple of integers.

        """
        widget = self.widget
        return (widget.width(), widget.height())

    def size_hint(self):
        """ Returns a (width, height) tuple of integers which represent
        the suggested size of the widget for its current state. This
        value is used by the layout manager to determine how much
        space to allocate the widget.

        """
        size_hint = self.widget.sizeHint()
        return (size_hint.width(), size_hint.height())

    def resize(self, width, height):
        """ Resizes the internal toolkit widget according the given
        width and height integers.

        """
        self.widget.resize(width, height)
    
    def set_min_size(self, min_width, min_height):
        """ Set the hard minimum width and height of the widget. A widget
        will not be able to be resized smaller than this value.

        """
        self.widget.setMinimumSize(min_width, min_height)

    def pos(self):
        """ Returns the position of the internal toolkit widget as an
        (x, y) tuple of integers. The coordinates should be relative to
        the origin of the widget's parent.

        """
        widget = self.widget
        return (widget.x(), widget.y())

    def move(self, x, y):
        """ Moves the internal toolkit widget according to the given
        x and y integers which are relative to the origin of the
        widget's parent.

        """
        self.widget.move(x, y)

    def geometry(self):
        """ Returns an (x, y, width, height) tuple of geometry info
        for the internal toolkit widget. The semantic meaning of the
        values are the same as for the 'size' and 'pos' methods.

        """
        x, y = self.pos()
        width, height = self.size()
        return (x, y, width, height)

    def set_geometry(self, x, y, width, height):
        """ Sets the geometry of the internal widget to the given
        x, y, width, and height values. The semantic meaning of the
        values is the same as for the 'resize' and 'move' methods.

        """
        self.widget.setGeometry(x, y, width, height)

    def on_resize(self):
        """ Triggers a relayout of the shell object since the component
        has been resized.

        """
        # Notice that we are calling do_layout() here instead of 
        # set_needs_layout() since we want the layout to happen
        # immediately. Otherwise the resize layouts will appear 
        # to lag in the ui. This is a safe operation since by the
        # time we get this resize event, the widget has already 
        # changed size. Further, the only geometry that gets set
        # by the layout manager is that of our children. And should
        # it be required to resize this widget from within the layout
        # call, then the layout manager will do that via invoke_later.
        self.shell_obj.do_layout()
    
    def shell_bg_color_changed(self, color):
        """ The change handler for the 'bg_color' attribute on the parent.
        Sets the background color of the internal widget to the given color.
        """
        role = self.widget.backgroundRole()
        self.set_role_color(role, color)
    
    def shell_fg_color_changed(self, color):
        """ The change handler for the 'fg_color' attribute on the parent.
        Sets the foreground color of the internal widget to the given color.
        For some widgets this may do nothing.
        """
        role = self.widget.foregroundRole()
        self.set_role_color(role, color)

    def shell_font_changed(self, font):
        """ The change handler for the 'font' attribute on the parent.
        Sets the font of the internal widget to the given font.
        For some widgets this may do nothing.
        """
        self.set_font(font)    

    #--------------------------------------------------------------------------
    # Convienence methods
    #--------------------------------------------------------------------------
    def parent_widget(self):
        """ Returns the logical QWidget parent for this component.

        Since some parents may wrap non-Widget objects, this method will
        walk up the tree of components until a QWidget is found or None
        if no QWidget is found.

        Returns
        -------
        result : QWidget or None

        """
        # XXX do we need to do this still? i.e. can we now have a parent
        # that doesn't create a widget???
        shell_parent = self.shell_obj.parent
        while shell_parent:
            widget = shell_parent.toolkit_widget
            if isinstance(widget, QtGui.QWidget):
                return widget
            shell_parent = shell_parent.parent

    def child_widgets(self):
        """ Iterates over the shell widget's children and yields the
        toolkit widgets for those children.

        """
        for child in self.shell_obj.children:
            yield child.toolkit_widget

    def set_role_color(self, role, color):
        """ Set the color for a role of a QWidget to the color specified by
        the given enaml color or reset the widgets color to the default value for
        the role if the enaml color is invalid.
        """
        if not color:
            palette = QtGui.QApplication.instance().palette(self.widget)
            qcolor = palette.color(role)
            # On OSX, the default color is rendered *slightly* off
            # so a simple workaround is to tell the widget not to
            # auto fill the background.
            if role == self.widget.backgroundRole():
                self.widget.setAutoFillBackground(False)
        else:
            qcolor = q_color_from_color(color)
            # When not using qt style sheets to set the background
            # color, we need to tell the widget to auto fill the 
            # background or the bgcolor won't render at all.
            if role == self.widget.backgroundRole():
                self.widget.setAutoFillBackground(True)
        palette = self.widget.palette()
        palette.setColor(role, qcolor)
        self.widget.setPalette(palette)

    def set_font(self, font):
        """ Set the font of the underlying toolkit widget to an appropriate
        QFont.
        """
        q_font = q_font_from_font(font)
        self.widget.setFont(q_font)
