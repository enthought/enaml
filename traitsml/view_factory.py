import types

from enthought.traits.api import (DelegatesTo, Dict, HasTraits, Instance, List,
                                  Str, Property, Tuple)

from .delegates import ViewDelegate
from .parsing import analyzer, tml_ast, tml_parser
from .registry import lookup_element
from .view_elements.element import Element

# This import causes all the view element modules to be imported
# which in turn cause them to be registered with the registry.
# No toolkit specific things are imported at this point. The only
# things created are the abstract traits classes.
from .view_elements import api


class View(HasTraits):
    """ Returned from the .create(...) function of a ViewFactory
    to create a view.

    """
    # The global namespace for this view tree, don't want to
    # pay the traits dict item overhead.
    _global_ns = Instance(dict, ())
    
    # The root view element
    _root_view = Instance(Element)

    # A list which holds the delegates for this view
    _delegates = List

    # Additional traits will be added via .add_trait(...),
    # one for each view element with a specified id.

    def __init__(self, factory_dict, file_ns, **ctxt_objs):
        super(View, self).__init__()
        self._global_ns.update(file_ns)
        self._global_ns.update(ctxt_objs)
        self._root_view = self.build_tree(factory_dict, parent=None)
            
    def show(self, app=False):
        # Let the toolkit do any startup necessary
        # XXX fill this in

        # Walk the tree and create all the toolkit specific widgets.
        self._root_view.init_widgets()
        
        # Now that the widgets are created, go through the delegates 
        # and have them bind any handlers they need.
        for delegate in self._delegates:
            delegate.bind()

        # Walk the tree again and initialize any attributes. 
        self._root_view.init_attributes()
        
        # Show the view.
        self._root_view.show()
        
        # Allow post-show layout to take place if required.
        self._root_view.init_layout()
        
        # And launch the toolkit app if necessary.
        # XXX fill this in
    
    def hide(self):
        self._root_view.hide()

    def build_tree(self, factory_dict, parent=None):
        """ Build a ui tree given a factory dict from the ViewFactory class.

        This method recursively descends the dict of dicts that is built
        by the ViewFactory class, and builds a tree of view element
        instances and hooks up the appropriate delegate handlers.

        The `parent` kwarg is used by this method to pass the current
        tree node during the recursive calls. The value should be None
        when creating a root node.

        """
        cls = factory_dict['class']
        identifier = factory_dict['identifier']
        assignments = factory_dict['assignments']
        bindings = factory_dict['bindings']
        notifications = factory_dict['notifications']
        pure_delegates = factory_dict['delegates']
        children = factory_dict['children']

        element = cls()
        delegate = ViewDelegate(element=element)
        global_ns = self._global_ns
        local_ns = {'self': element, 'parent': parent}
        
        # Assignments
        for trait_name, code in assignments:
            delegate.add_assignment(trait_name, code, global_ns, local_ns)
        
        # Bindings
        for trait_name, code, deps in bindings:    
            delegate.add_binding(trait_name, code, global_ns, local_ns, deps)
    
        # Notifications
        for trait_name, code in notifications:
            delegate.add_notifier(trait_name, code, global_ns, local_ns)
        
        # Before we build children, we need to add ourselves to the
        # global namespace in case the children have pure delegates that 
        # reference us. Also we add the element as a trait on the view 
        # so it can be accessed by name as a convienence for user code.
        if identifier is not None:
            self.add_trait(identifier, element)
            self._global_ns[identifier] = element 

        # A pure delegate may reference an object that is a child and
        # thus is not yet defined. So, we need to create the children 
        # first so that they will be available in the global namespace
        # and therefore referenceable.
        for child in children:
            child_elem = self.build_tree(child, parent=element)
            element.children.append(child_elem)

        # Pure Delegates
        for trait_name, obj_name, attr_name in pure_delegates:
            obj = local_ns.get(obj_name) or global_ns.get(obj_name)
            if obj is None:
                raise NameError('Name `%s` is not defined.' % obj_name)
            delegate.add_delegate(trait_name, obj, attr_name)
        
        self._delegates.append(delegate)

        return element


class ViewFactory(HasTraits):
    
    # The path to the .tml file
    tml_filename = Str

    # The parsed tml AST
    tml_ast = Instance(tml_ast.TML)

    # The global namespace for the .tml file. Will contain imports
    # and builtins, and is used as the base for instance specific
    # global namespaces.
    file_ns = Dict
    
    # The toplevel node id's mapping to a factory dicts. This will be a 
    # tree of classes, code, objects, and dependency strings to speed 
    # the instantiation of new instances of the view.
    factory_dicts = Instance(dict, ())
    
    def __init__(self, tml_filename):
        super(ViewFactory, self).__init__()
        self.tml_filename = tml_filename
        self._parse()
    
    def __call__(self, identifier, **ctxt_objs):
        if identifier not in self.factory_dicts:
            msg = 'Toplevel element `%s` not defined.' % toplevel_id
            raise ValueError(msg)
        factory_dict = self.factory_dicts[identifier]
        return View(factory_dict, self.file_ns, **ctxt_objs)

    def _parse(self):
        tml_text = open(self.tml_filename).read()
        ast = tml_parser.parse(tml_text)
        self.tml_ast = ast

        # Separate imports from toplevel elements. The parser guarantees
        # that the ast body is composed of only imports or elements.
        for item in ast.body:
            if isinstance(item, tml_ast.TMLImport):
                code = compile(item.ast_mod, self.tml_filename, mode='exec')
                exec code in self.file_ns
            else:
                self._make_toplevel_factory(item)
        
        # Make a final pass through the factories to make sure all
        # identifiers are unique. We already know the toplevel identifiers
        # are unique, so we just need to check the children.
        seen_ids = set()
        duplicates = set()
        stack = self.factory_dicts.values()
        while stack:
            dct = stack.pop()
            identifier = dct['identifier']
            if identifier:
                if identifier in seen_ids:
                    duplicates.add(identifier)
                else:
                    seen_ids.add(identifier)
            stack.extend(dct['children'])

        if duplicates:
            msg = 'Duplicate use of identifier(s): %s.' % (tuple(duplicates),)
            raise ValueError(msg)

    def _make_toplevel_factory(self, element):
        # element will be an instance of a TMLElement node, which
        # we'll parse into a toplevel factory. This parsing consists
        # of expanding the node in a tree of view element classes, 
        # compiled code objects, and dependency specifications. 
        # This tree will be used when .create(...) is called to 
        # create an instance of the view.
        factory_dict = self._make_factory(element)
        identifier = factory_dict['identifier']
        if identifier is None:
            msg = 'Toplevel view elements must have an identifier.'
            raise ValueError(msg)

        if identifier in self.factory_dicts:
            raise ValueError('Duplicate use of identifer `%s`.' % identifier)

        self.factory_dicts[identifier] = factory_dict

    def _make_factory(self, element):
        # Recursively creates the factory dict for this element and all
        # of it's children. 
        factory_dict = {'class': None,
                        'identifier': None,
                        'assignments': [],
                        'bindings': [],
                        'delegates': [],
                        'notifications': [],
                        'children': []}
        
        factory_dict['class'] = lookup_element(element.name)
        factory_dict['identifier'] = element.identifier

        # Separate the children from the assignments and compile 
        # the assignment expressions
        for item in element.body:
            if isinstance(item, tml_ast.TMLElement):
                child = self._make_factory(item)
                factory_dict['children'].append(child)
            elif isinstance(item, tml_ast.TMLAssign):
                name = item.name
                expr = item.expr
                code = compile(expr, self.tml_filename, mode='eval')
                factory_dict['assignments'].append((name, code))
            elif isinstance(item, tml_ast.TMLBind):
                name = item.name
                expr = item.expr
                attrs = analyzer.attributes(expr)
                code = compile(expr, self.tml_filename, mode='eval')
                factory_dict['bindings'].append((name, code, attrs))
            elif isinstance(item, tml_ast.TMLNotify):
                name = item.name
                expr = item.expr
                code = compile(expr, self.tml_filename, mode='eval')
                factory_dict['notifications'].append((name, code))
            elif isinstance(item, tml_ast.TMLDelegate):
                name = item.name
                obj_name = item.obj_name
                attr_name = item.attr_name
                factory_dict['delegates'].append((name, obj_name, attr_name))
            else:
                raise TypeError('Unkown TML ast node %s' % item)

        return factory_dict


 
