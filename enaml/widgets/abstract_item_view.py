#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from abc import abstractmethod

from traits.api import Bool, Event, Instance

from .control import Control, AbstractTkControl

from ..item_models.abstract_item_model import AbstractItemModel
from ..item_models.model_index import ModelIndex
from .base_selection_model import BaseSelectionModel


class AbstractTkItemView(AbstractTkControl):
    
    @abstractmethod
    def shell_item_model_changed(self, model):
        raise NotImplementedError


class AbstractItemView(Control):
    """ An abstract base class view that contains common logic for the
    ListView, TableView, and TreeView classes.
    
    """
    #: The AbstractItemModel instance being displayed by the view.
    item_model = Instance(AbstractItemModel)

    #: The selection model for this view.
    selection_model = Instance(BaseSelectionModel, args=())

    #: The ModelIndex that has just been activated by a user interaction,
    #: usually a double-click or an Enter keypress.
    activated = Event(Instance(ModelIndex))

    #: The ModelIndex that has just been clicked.
    clicked = Event(Instance(ModelIndex))

    #: The ModelIndex that has just been double-clicked.
    double_clicked = Event(Instance(ModelIndex))

    #: Overridden parent class trait
    abstract_obj = Instance(AbstractTkItemView)

    # Whether the selection model has been provided by the Enaml syntax or not.
    # Keeping track of this let's us prevent two or more selection models being
    # provided.
    _has_child_selection_model = Bool(False)


    def add_subcomponent(self, component):
        """ Adds the given component as a subcomponent of this object.

        Overridden to pull out the single selection model.

        """
        if self._has_child_selection_model:
            msg = "Already have one child selection model."
            raise ValueError(msg)
        if not isinstance(component, BaseSelectionModel):
            msg = ("Expected an instance of {0.__name__}, got {1!r} {2!r} "
                "instead.".format(BaseSelectionModel, component, type(component)))
            raise TypeError(msg)
        self.trait_set(
            selection_model=component,
            _has_child_selection_model=True,
        )

    def _setup_parent_refs(self):
        """ A setup method which assigns the parent reference to the
        child subcomponents.

        """
        child = self.selection_model
        child.parent = self
        child._setup_parent_refs()

    def _setup_create_widgets(self, parent):
        """ A setup method that, by default, is a no-op. Subclasses 
        that drive gui toolkit widgets should reimplement this method
        to create the underlying toolkit widget(s).

        """
        self.abstract_obj.create(parent)
        self_widget = self.toolkit_widget
        self.selection_model._setup_create_widgets(self_widget)

    def _setup_init_widgets(self):
        """ A setup method that, by default, is a no-op. Subclasses 
        that drive gui toolkit widgets should reimplement this method
        to initialize their internal toolkit widget(s).

        """
        self.abstract_obj.initialize()
        self.selection_model._setup_init_widgets()

    def _setup_eval_expressions(self):
        """ A setup method that loops over all of bound expressions and
        performs a getattr for those attributes. This ensures that all
        bound attributes are initialized, even if they weren't implicitly
        initialized in any of the previous setup methods.

        """
        for name in self._expressions:
            getattr(self, name)
        self.selection_model._setup_eval_expressions()

    def _setup_bind_widgets(self):
        """ A setup method that, by default, is a no-op. Subclasses 
        that drive gui toolkit widgets should reimplement this method
        to bind any event handlers of their internal toolkit widget(s).

        """
        self.abstract_obj.bind()
        self.selection_model._setup_bind_widgets()

    def _setup_listeners(self):
        """ A setup method that, by default, is a no-op. Subclasses 
        that drive gui toolkit widgets should reimplement this method
        to setup an traits listeners necessary to drive their internal
        toolkit widget(s).

        """
        self.add_trait_listener(self.abstract_obj, 'shell')
        self.selection_model._setup_listeners()

    def _setup_init_visibility(self):
        """ A setup method that, by default, is a no-op. Subclasses 
        that drive gui toolkit widgets should reimplement this method
        to initialize the visibility of their widgets.

        """
        self.set_visible(self.visible)

    def _setup_init_layout(self):
        """ A setup method that, by default, is a no-op. Subclasses 
        that manage layout should reimplement this method to initialize
        their underlying layout.

        """
        self.initialize_layout()

    def _setup_set_initialized(self):
        """ A setup method which updates the initialized attribute of 
        the component to True.

        """
        self.initialized = True
        self.selection_model._setup_set_initialized()


