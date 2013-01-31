#------------------------------------------------------------------------------
# Copyright (c) 2013, Enthought, Inc.
# All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Any, Bool, Enum, Str, Unicode, Int, Long, Float

from enaml.core.declarative import Declarative, scope_lookup
from enaml.core.templated import Templated


class ItemEditor(Declarative):
    """ A base class for creating item editors.

    """
    #: The value of the editor. Subclasses may redefine this trait.
    value = Any

    #: The tool tip to use for the item.
    tool_tip = Unicode

    #: The status tip to use for the item.
    status_tip = Unicode

    #: The background color of the item. Supports CSS3 color strings.
    background = Str

    #: The foreground color of the item. Supports CSS3 color strings.
    foreground = Str

    #: The font of the item. Supports CSS3 shorthand font strings.
    font = Str

    #: Whether or not the item can be checked by the user. This has no
    #: bearing on whether or not a checkbox is visible for the item.
    #: For controlling the visibility of the checkbox, see `checked`.
    checkable = Bool(False)

    #: Whether or not the item is checked. A value of None indicates
    #: that no check box should be visible for the item.
    checked = Enum(None, False, True)

    #: Whether or not the item can be selected.
    selectable = Bool(True)

    #: Whether or not the item is selected. This value only has meaning
    #: if 'selectable' is set to True.
    selected = Bool(False)

    #: Whether or not the item is editable.
    editable = Bool(True)

    #: Whether or not the item is enabled.
    enabled = Bool(True)

    #: Private storage for the toolkit data. This can be used by a
    #: toolkit backend to store anything its needs on the editor.
    _toolkit_data = Any


class StringEditor(ItemEditor):
    """ An `ItemEditor` subclass for editing plain strings.

    """
    #: The value of the editor.
    value = Str


class UnicodeEditor(ItemEditor):
    """ An `ItemEditor` subclass for editing unicode strings.

    """
    #: The value of the editor.
    value = Unicode


class IntEditor(ItemEditor):
    """ An `ItemEditor` subclass for editing integers.

    """
    #: The value of the editor.
    value = Int


class LongEditor(ItemEditor):
    """ An `ItemEditor` subclass for editing longs.

    """
    #: The value of the editor.
    value = Long


class FloatEditor(ItemEditor):
    """ An `ItemEditor` subclass for editing floats.

    """
    #: The value of the editor.
    value = Float


class BoolEditor(ItemEditor):
    """ An `ItemEditor` subclass for editing bools.

    """
    #: The value of the editor.
    value = Bool


class EditGroup(Templated):
    """ A templated object which manages `ItemEditor` children.

    """

    #: An internal flag indicating whether the children have been built.
    _built = Bool(False)

    def item_editors(self):
        """ Get the item editors defined on this group.

        This method will trigger the creation of the group's children
        the first time it is called.

        Returns
        -------
        result : generator
            A generator which will yield the children of the group
            which are instances of `ItemEditor`.

        """
        if not self._built:
            self._build()
        for child in self.children:
            if isinstance(child, ItemEditor):
                yield child

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _build(self):
        """ Create and initialize the templated children of the group.

        This method will set the `_built` flag to True, then build
        and initialize the children.

        """
        self._built = True
        with self.children_event_context():
            for identifiers, f_globals, descriptions in self._templates:
                scope = identifiers.copy()
                for descr in descriptions:
                    cls = scope_lookup(descr['type'], f_globals, descr)
                    instance = cls(self)
                    with instance.children_event_context():
                        instance.populate(descr, scope, f_globals)
                    instance.initialize()


class ModelEditor(Declarative):
    """ A class for editing a model using `EditGroup` children.

    """
    #: The model object for the editor. This is provided as a developer
    #: convenience since most editors will require a reference to the
    #: model they are editing. Subclasses may redefine this trait.
    model = Any

    def edit_groups(self):
        """ Get the edit groups defined on this group.

        Returns
        -------
        result : generator
            A generator which will yield the children of the editor
            which are instances of `EditGroup`.

        """
        for child in self.children:
            if isinstance(child, EditGroup):
                yield child

