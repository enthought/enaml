import re
import itertools
import functools

from traits.api import (HasStrictTraits, HasTraits, Instance, Event, Interface, 
                        Str, Dict, Any, Set, Int, on_trait_change, Property)


# Matches the '*' selector
DEFAULT_SELECTOR = re.compile(r'(\*)$')

# Matches a type selector like 'PushButton'
TYPE_SELECTOR = re.compile(r'([a-zA-Z_][a-zA-Z0-9_]*)$')

# Matches a class selector like '.expanding.error.underline' or '*.normal'
CLASS_SELECTOR = re.compile(r'((?:\.[a-zA-Z_][a-zA-Z0-9_]*)*)$')

# Matches type qualified classes like 'Html.error_colors'
QUAL_SELECTOR = re.compile(r'([a-zA-Z_][a-zA-Z0-9_]*)((?:\.[a-zA-Z_][a-zA-Z0-9_]*)*)$')

#CHILD_RE = re.compile(r'([a-zA-Z_][a-zA-Z0-9_]*)\.?([a-zA-Z_][a-zA-Z0-9_]*)\s*>\s*([a-zA-Z_][a-zA-Z0-9_]*)$')

# Matches an id selector like "#my_push_button"
ID_SELECTOR = re.compile(r'(#[a-zA-Z_][a-zA-Z0-9_]*)$')

# A sentinel object for indicating no style.
class NO_STYLE(object):
    __slots__ = ()
    def __repr__(self):
        return self.__class__.__name__
    def __str__(self):
        return repr(self)
    def __nonzero__(self):
        return False
NO_STYLE = NO_STYLE()


class style(object):
    """ An object which represents a style declaration in a style sheet.

    """
    __slots__ = ('selectors', 'properties')

    def __init__(self, *selectors, **properties):
        """ Constructs a style object.

        Parameters
        ----------
        *selectors
            A sequence of string following the selector syntax.
        
        **properties
            A sequence of keywords specifiying the styling values.

        """
        self.selectors = tuple(selector.strip() for selector in selectors)
        self.properties = properties


class IStyleNodeData(Interface):
    """ An interface used by the style sheet selectors to query for 
    the styling information required to perform a match.

    """
    def node_id(self):
        """ Returns the id of the element being styled as a string.

        """
        raise NotImplementedError
    
    def node_classes(self):
        """ Returns the classes of the element being styled as a space
        separated string.

        """
        raise NotImplementedError
    
    def node_type(self):
        """ Returns the type of the element being styled as a string.

        """
        raise NotImplementedError

    def parent_node(self):
        """ Returns an IStyleQuery object for the parent element of the
        element being styled.

        """
        raise NotImplementedError
    

class Selector(HasStrictTraits):
    """ A Selector for use in the StyleSheet.

    The base Selector class is used as the default match-all selector.
    Subclasses can override the match() method to implemented more
    restrictive selectors.

    Attributes
    ----------
    properies : Dict(Str, Any)
        The style properties for this match.

    order : Int
        A integer which is modified by the style sheet to maintain
        information about the order in which selectors appear.

    touch : Int
        A value that is incremented by the style sheet whenever the 
        selector is updated. This helps to break ties between selectors
        that match with identical specificity.

    Methods
    -------
    match(style_query)
        Returns a tuple of (specificity, is_match).

    """
    properties = Dict(Str, Any)

    order = Int

    def match(self, node_data):
        """ Returns the match of the selector for the given query.

        Arguments
        ---------
        node_data : IStyleNodeData
            An object for the node being styled which implements the 
            IStyleNodeData interface.
        
        Returns
        -------
        result : bool, (int, properties)
            If first return value is False, the selector does not match 
            the node. Otherwise, the second return value is a tuple of 
            (specificity, order, properties).

        """
        return True, (0, self.order, self.properties)


class TypeSelector(Selector):
    """ A style selector which matches element types.

    See Also
    --------
    Selector

    """
    node_type = Str

    def match(self, node_data):
        match = node_data.node_type() == self.node_type
        return match, (1, self.order, self.properties)


class ClassSelector(Selector):
    """ A style selector which matches style classes.

    See Also
    --------
    Selector

    """
    node_classes = Instance(set)

    def match(self, node_data):
        these_classes = self.node_classes
        specificity = 0
        for node_class in node_data.node_classes().split():
            if node_class in these_classes:
                specificity += 10
        match = bool(specificity)
        return match, (specificity, self.order, self.properties)


class QualSelector(Selector):
    """ A style selector which matches type qualified classes.

    See Also
    --------
    Selector

    """
    node_type = Str

    node_classes = Instance(set)

    def match(self, node_data):
        match = False
        specificity = 0
        type_match = node_data.node_type() == self.node_type
        if type_match:
            these_classes = self.node_classes
            for node_class in node_data.node_classes().split():
                if node_class in these_classes:
                    specificity += 10
            # the type only counts if we have class matches
            if specificity > 0:
                specificity += 1
        match = bool(specificity)
        return match, (specificity, self.order, self.properties)


class IDSelector(Selector):
    """ A style selector which matches element ids.

    See Also
    --------
    Selector

    """
    node_id = Str

    def match(self, node_data):
        match = node_data.node_id() == self.node_id
        return match, (100, self.order, self.properties)


class StyleSheet(HasStrictTraits):
    """ An object representing a style sheet.

    The style sheet is constructed with a sequence of 'style' objects
    which are then parsed into an internal dictionary of selectors.
    The value for a style property which matches style criteria can be
    retrieved through the 'get_property' method.

    Attributes
    ----------
    updated : Event
        An event which is fired when the style sheet has changed. The 
        payload of the event will be a set of property names that have 
        been updated. This event is not fired when the sheet is first 
        instantiated.
    
    Methods
    -------
    update(*styles)
        Update the style sheet with the given style objects. This 
        will trigger an 'updated' event.
    
    replace(*styles)
        Replace the style sheet with the give style objects. This
        will trigger an 'updated' event.

    """
    # Maps the style selector string to the created Selector object.
    _selectors = Dict(Str, Instance(Selector))

    # Maps a property name to the set of Selectors 
    # which contain a property with that name.
    _property_selectors = Dict(Str, Set(Instance(Selector)))

    # A counter that is used
    _counter = Instance(itertools.count, ())

    updated = Event

    def __init__(self,  *styles):
        """ Construct a style sheet object.

        Parameters
        ----------
        *styles : Sequence of 'style' objects.
            The style objects with which to populate the sheet.

        """
        super(StyleSheet, self).__init__()
        self._selectors = {}
        self._property_selectors = {}
        self._parse_styles(*styles)

    def _parse_styles(self, *styles):
        """ A private method which parses the styles in the appropriate
        selector objects.

        """
        selector_map = self._selectors
        counter = self._counter
        updated_selectors = set()

        for sty in styles:

            selector_strings = sty.selectors
            properties = sty.properties

            for selector_str in selector_strings:
                
                match = TYPE_SELECTOR.match(selector_str)
                if match:
                    match_str = match.group(1)
                    if match_str in selector_map:
                        selector = selector_map[match_str]
                    else:
                        selector = TypeSelector(node_type=match_str)
                        selector_map[match_str] = selector
                    selector.order = counter.next()
                    selector.properties.update(properties)
                    updated_selectors.add(selector)
                    continue  

                match = CLASS_SELECTOR.match(selector_str)
                if match:
                    match_str = match.group(1)
                    if match_str in selector_map:
                        selector = selector_map[match_str]
                    else:
                        node_classes = set(filter(None, match_str.split('.')))
                        selector = ClassSelector(node_classes=node_classes)
                        selector_map[match_str] = selector
                    selector.order = counter.next()
                    selector.properties.update(properties)
                    updated_selectors.add(selector)
                    continue

                match = QUAL_SELECTOR.match(selector_str)
                if match:
                    match_str = selector_str
                    if match_str in selector_map:
                        selector = selector_map[match_str]
                    else:
                        node_type, rest = match_str.split('.', 1)
                        node_classes = set(rest.split('.'))
                        selector = QualSelector(node_type=node_type,
                                                node_classes=node_classes)
                        selector_map[match_str] = selector
                    selector.order = counter.next()
                    selector.properties.update(properties)
                    updated_selectors.add(selector)
                    continue

                match = ID_SELECTOR.match(selector_str)
                if match:
                    match_str = match.group(1)
                    if match_str in selector_map:
                        selector = selector_map[match_str]
                    else:
                        selector = IDSelector(node_id=match_str[1:])
                        selector_map[match_str] = selector
                    selector.order = counter.next()
                    selector.properties.update(properties)
                    updated_selectors.add(selector)
                    continue

                match = DEFAULT_SELECTOR.match(selector_str)
                if match:
                    match_str = match.group(1)
                    if match_str in selector_map:
                        selector = selector_map[match_str]
                    else:
                        selector = Selector()
                        selector_map[match_str] = selector
                    selector.order = counter.next()
                    selector.properties.update(properties)
                    updated_selectors.add(selector)
                    continue
        
        property_selectors = self._property_selectors
        updated_properties = set()
        for selector in updated_selectors:
            for key in selector.properties:
                property_selectors.setdefault(key, set()).add(selector)
                updated_properties.add(key)

        return updated_properties

    def update(self, *styles):
        """ Update the style sheet with the given style objects. 

        This will trigger a 'sheet_updated' event.

        Parameters
        ----------
        *styles : Sequence of 'style' objects.
            The style objects with which to update the sheet.

        """
        self.updated = self._parse_styles(*styles)

    def replace(self, *styles):
        """ Replace the style sheet with the give style objects. 

        This will trigger a 'sheet_replaced' event.

        Parameters
        ----------
        *styles : Sequence of 'style' objects.
            The style objects with which to populate the sheet.

        """
        self._selectors = {}
        self._property_selectors = {}
        self._counter = itertools.count()
        self.updated = self._parse_styles(*styles)

    def get_property(self, tag, node_data):
        """ Returns the style property for the given tag.

        This method is used to query the style sheet for the value of a
        property for a particular node as described by the given style
        node data object.

        Arguments
        ---------
        node_data : IStyleNodeData
            An object for the node being styled which implements the 
            IStyleNodeData interface.

        Returns
        -------
        result : style property or NO_STYLE
            Returns the style property for the most specific match of
            the sheet, or NO_STYLE if no match is found.

        """
        selectors = self._property_selectors.get(tag)
        if not selectors:
            return NO_STYLE

        matches = (selector.match(node_data) for selector in selectors)
        specs = (spec for match, spec in matches if match)
            
        # If there are no matches, max will bail on the empty sequence.
        try:
            res = max(specs)[2][tag]
        except ValueError:
            res = NO_STYLE

        return res

    def get_tags(self):
        """ Returns an iterable of all the tags in the style_sheet.

        """
        return self._property_selectors.iterkeys()

    def has_tag(self, tag):
        """ Returns True or False depending on whether the tag is in the
        style sheet.

        """
        return tag in self._property_selectors


#-------------------------------------------------------------------------------
# Style Node and Handler
#-------------------------------------------------------------------------------
class StyleNode(HasTraits):
    """ A basic style node class meant for subclassing.

    StyleNode provides much of the boiler plate needed to integrate 
    style sheet support with other objects. It will search for the 
    style object on the class first, then the style sheet. This allows
    for selectively overriding style sheet values without modifying the
    style sheet itself. A complete solution will use a subclass of 
    StyleNode along with a subclass of StyleHandler.

    Attributes
    ----------
    style_sheet : Instance(StyleSheet)
        The StyleSheet on which this node is operating.
    
    node_data : Property(Instance(IStyleNodeData))
        A property whose getter returns an implementor of IStyleNodeData.
        The getter must be implemented by subclasses.
    
    tag_updated : Event
        A event fired when a tag in the style sheet is updated. The 
        event payload is the tag name that was updated.

    Methods
    -------
    refresh_tags(tags)
        Refresh all of the tags in the given sequence of tags.

    get_property(tag)
        Returns the style property for the given tag.
    
    """
    style_sheet = Instance(StyleSheet)

    node_data = Property(Instance(IStyleNodeData))

    tag_updated = Event

    def _get_node_data(self):
        """ The propery getter for node_data attribute. This should be
        implemented by subclasses to return an object that implements 
        IStyleNodeData.

        """
        raise NotImplementedError

    @on_trait_change('style_sheet:updated')
    def _style_sheet_updated(self, updated):
        """ Refreshes the tags for the sequence of updated tags.

        """
        self.refresh_tags(updated)

    @on_trait_change('style_sheet')
    def _style_sheet_swapped(self):
        """ Refreshes the tags for every tag in the sheet.

        """
        self.refresh_tags(self.style_sheet.get_tags())
    
    def refresh_tags(self, tags):
        """ Triggers the 'tag_updated' event for each of the given tags.

        """
        for tag in tags:
            self.tag_updated = tag

    def get_property(self, tag):
        """ Returns the style property for the given tag.

        Looks first on self, then queries the style sheet if that lookup
        fails. This allows subclasses to selectively override the style
        sheet.

        Parameters
        ----------
        tag : string
            The property tag to lookup.

        Returns
        -------
        result : object
            The style property or NO_STYLE

        """
        try:
            res = getattr(self, tag)
        except AttributeError:
            res = self.style_sheet.get_property(tag, self.node_data)
        return res


class StyleHandler(HasStrictTraits):
    """ A handler class that reacts to changes on a StyleNode.

    This StyleHandler is meant to be used in conjuction with subclasses
    of StyleNode. It reacts to changes on the events of the StyleNode
    and dispatches to specially named handler methods on the subclass.
    The dispatching is done efficiently so that the style sheet is 
    only queried if a handler for the tag exists, and the handler is
    only called if the value has changed.

    Attributes
    ----------
    node : Instance(StyleNode)
        The StyleNode instance this object is handling.

    tags : dict, optional
        A dictionary of string tags to arguments to pass to the 
        set_style_value method on subclasses.

    Methods
    -------
    style_*
        Subclasses should implement a style_* method for every tag for
        which updates are desired.

    set_style_value(self, value, tag, *args)
        A method that can be optionally implemented by subclasses for
        easier style dispatching. If a tag is defined in the `tags` dict 
        and the subclass does not define adefault a style_<tag> method, 
        then set_style_value will be called with the (value, tag, *args) 
        where the *args are the args that key in the dict. 

    """
    node = Instance(StyleNode)

    tags = Instance(dict, ())
    
    _style_dict = Instance(dict, ())

    @on_trait_change('node:tag_updated')
    def _tag_updated(self, tag):
        """ Handles the tag_updated event on the style node.

        """
        self._update_tag(tag)
        
    def set_style_value(self, value, tag, *args):
        """ Set the style given by the tag to the value in a generic way.
        
        This is intended to simplify definition of style handlers for a toolkit
        where a lot of the code is doing the same sort of thing.
        
        Arguments
        ---------
        value : style_value
            The string representation of the style's value.
        
        tag : string
            The style tag that is being set.
        
        *args
            Additional arguments as needed.  This is likely to include a
            converter function and/or the method name to set.
        
        Returns
        -------
        result : None

        Notes
        -----
        This method will only be called if the tag exists in the `tags` 
        dict and there is no style_<tag> handler defined for it.

        """
        raise NotImplementedError
    
    def initialize_style(self):
        """ Initialize all style properties handled by methods or tags.

        """
        style_handlers = {}
        for name in dir(self):
            if name.startswith('style_'):
                style_handlers[name] = getattr(self, name)
        
        node = self.node
        
        for tag, handler in style_handlers.iteritems():
            value = node.get_property(tag)
            handler(value)
        
        for tag, args in self.tags.items():
            if tag in style_handlers:
                continue
            if not isinstance(args, (list, tuple)):
                args = (args,)
            value = node.get_property(tag)
            self.set_style_value(value, tag, *args)
        
    def _update_tag(self, tag, null=object()):
        """ Dispatches a tag update to specially named methods. Only
        dispatches if a handler exists and the value has changed.

        """
        name = 'style_' + tag
        handler = getattr(self, name, None)
        tags = self.tags

        if handler is None and tag in tags:
            args = tags[tag]
            if not isinstance(args, (list, tuple)):
                args = (args,)

            def handler(value):
                return self.set_style_value(value, tag, *args)
        
        if handler is not None:
            style_dict = self._style_dict
            old = style_dict.get(tag, null)
            new = self.node.get_property(tag)
            if old != new:
                style_dict[tag] = new
                handler(new)

