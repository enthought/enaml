import re
import itertools

from traits.api import (MetaHasTraits, HasStrictTraits, HasTraits, Instance, 
                        Event, Interface, Str, Dict, Any, Set, Int, TraitType,
                        on_trait_change)


# Matches the '*' selector
DEFAULT_SELECTOR = re.compile(r'(\*)$')

# Matches a type selector like 'PushButton'
TYPE_SELECTOR = re.compile(r'([a-zA-Z_][a-zA-Z0-9_]*)$')

# Matches a class selector like '.expanding.error.underline' or '*.normal'
CLASS_SELECTOR = re.compile(r'((?:\.[a-zA-Z_][a-zA-Z0-9_]*)*)$')

#QUAL_RE = re.compile(r'([a-zA-Z_][a-zA-Z0-9_]*)\.([a-zA-Z_][a-zA-Z0-9_]*)$')

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
                specificity += 1
        match = bool(specificity)
        return match, (specificity * 10, self.order, self.properties)


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


class StyleTrait(TraitType):
    """ A trait to lookup style properties from a style sheet.

    A StylePropertyLookup behaves like a read-only trait and will 
    query a StyleSheet for the value of a property tag each time 
    the trait is accessed. No caching of the results is done, since 
    the lookup is not a very expensive operation and we would rather
    save the memory.

    """
    def __init__(self, sheet_trait, data_trait, tag=None):
        """ Construct a StylePropertyLookup traits.

        Parameters
        ----------
        sheet_trait : string
            The name of the trait on the object which contains the 
            style sheet.

        data_trait : string
            The name of the trait on the object which contains an
            IStyleNodeData object to use for the matching.
        
        tag : string, optional
            The property tag to query for this attribute, if not given
            the tag will be the name to which this trait is assigned.

        """
        super(StyleTrait, self).__init__()
        if not isinstance(sheet_trait, basestring):
            raise TypeError('`sheet_trait` should be a string.')
        if not isinstance(data_trait, basestring):
            raise TypeError('`data_trait` should be a string.')
        if tag is not None:
            if not isinstance(tag, basestring):
                raise TypeError('`tag` should be a string or None.')
        self.sheet_trait = sheet_trait
        self.data_trait = data_trait
        self.tag = tag

    def get(self, obj, name):
        tag = self.tag
        if tag is None:
            tag = name            
        sheet = getattr(obj, self.sheet_trait)
        data = getattr(obj, self.data_trait)
        return sheet.get_property(tag, data)


class ReactiveStyleNodeMeta(MetaHasTraits):

    def __new__(meta, name, bases, cls_dict):
        cls = MetaHasTraits.__new__(meta, name, bases, cls_dict)
        style_traits = set()
        for name, trait in cls.__class_traits__.iteritems():
            trait_type = trait.trait_type
            if isinstance(trait_type, StyleTrait):
                style_traits.add(name)
        cls.__style_traits__ = style_traits
        return cls


class ReactiveStyleNode(HasTraits):

    __metaclass__ = ReactiveStyleNodeMeta

    @on_trait_change('style_sheet:updated')
    def _notify_updated_styles(self, updated_styles):
        style_traits = self.__style_traits__
        for name in updated_styles:
            if name in style_traits:
                self.trait_property_changed(name, None, getattr(self, name))
    
    def _style_sheet_changed(self):
        for name in self.__style_traits__:
            self.trait_property_changed(name, None, getattr(self, name))

