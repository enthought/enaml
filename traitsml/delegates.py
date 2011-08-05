import types
import weakref

from enthought.traits.api import (Any, Bool, CTrait, DelegatesTo, Event, HasStrictTraits, 
                                  HasTraits, Instance, List, Property, Str, Tuple)


class Notifier(HasStrictTraits):
    
    # The code object that holds the expression.
    code = Instance(types.CodeType)

    # The global namespace for the code. 
    global_ns = Instance(dict)

    # The local namespace for the code.
    local_ns = Instance(dict)

    def notify(self):
        # This is called by ViewDelegate when the expression 
        # should be evaluated because the associated view element 
        # trait has changed.
        eval(self.code, self.global_ns, self.local_ns)


class Assignment(HasStrictTraits):
    
    # The code object that holds the expression.
    code = Instance(types.CodeType)

    # The global namespace for the code. 
    global_ns = Instance(dict)

    # The local namespace for the code.
    local_ns = Instance(dict)
    
    # The trait used to validate the default.
    validate_trait = Instance(CTrait)
    
    # The actual trait that holds the value.
    value = Any
    
    def _value_default(self):
        val = eval(self.code, self.global_ns, self.local_ns)
        val = self.validate_trait.validate(self, 'value', val)
        return val


class Binding(HasStrictTraits):
    
    # The code object that holds the expression.
    code = Instance(types.CodeType)

    # The global namespace for the code. 
    global_ns = Instance(dict)

    # The local namespace for the code.
    local_ns = Instance(dict)
    
    # The trait used to validate the default.
    validate_trait = Instance(CTrait)
    
    # The actual trait that holds the value.
    value = Any
    
    def _value_default(self):
        val = eval(self.code, self.global_ns, self.local_ns)
        val = self.validate_trait.validate(self, 'value', val)
        return val
    
    def update_value(self):
        # This will be called when any of the dependencies 
        # in the expression change. The listeners are hooked
        # up by ViewDelegate.
        val = eval(self.code, self.global_ns, self.local_ns)
        val = self.validate_trait.validate(self, 'value', val)
        self.value = val 


class Delegate(HasStrictTraits):

    # The object to which we are delegating.
    obj = Instance(HasTraits)

    # The trait name on the object to which we are delegating.
    trait_name = Str

    # The trait used to validate the default.
    validate_trait = Instance(CTrait)
    
    # The actual trait that holds the value.
    value = Property(depends_on='_value_trigger')

    # The trigger which will set off a value change
    _value_trigger = Event

    def _get_value(self):
        val = getattr(self.obj, self.trait_name)
        val = self.validate_trait.validate(self, 'value', val)
        return val

    def _set_value(self, val):
        setattr(self.obj, self.trait_name, val)

    def update_value(self):
        self._value_trigger = True


class ViewDelegate(HasStrictTraits):
    
    # The view element for which we are providing delegation.
    element = Instance(HasTraits)
        
    # The list of notifier objects (ala the tml keyword `notify`).
    notifiers = List

    # The list of assignment objects.
    assignments = List

    # The list of binding objects.
    bindings = List
    
    # The list of delegate objects.
    delegates = List

    # This will contain a list of callable objects that will perform
    # the binding when necessary. It will then be deleted to free 
    # the closures.
    _binders = List

    def add_notifier(self, trait_name, code, global_ns, local_ns):
        notifier = Notifier(code=code, global_ns=global_ns, local_ns=local_ns)

        def binder():
            self.element.on_trait_change(notifier.notify, trait_name)

        self._binders.append(binder)
        self.notifiers.append(notifier)

    def add_assignment(self, trait_name, code, global_ns, local_ns):
        validate_trait = self._valid_intercept(trait_name)
        assignment = Assignment(validate_trait=validate_trait, code=code, 
                                global_ns=global_ns, local_ns=local_ns)

        def binder():
            element = self.element
            delegate_name = '_' + trait_name + '_delegate'
            element.add_trait(delegate_name, assignment)
            element.add_trait(trait_name, DelegatesTo(delegate_name, 'value'))
            element.trait_added = trait_name

        self._binders.append(binder)
        self.assignments.append(assignment)
    
    def add_binding(self, trait_name, code, global_ns, local_ns, dependencies):
        validate_trait = self._valid_intercept(trait_name)
        binding = Binding(validate_trait=validate_trait, code=code, 
                          global_ns=global_ns, local_ns=local_ns)
        
        
        def binder():
            for dep in dependencies:
                obj_name, extended_name = dep
                obj = local_ns.get(obj_name) or global_ns.get(obj_name)
                if obj is None:
                    msg = '`%s` is not defined or accessible in the view.'
                    raise NameError(msg % obj_name)
                if isinstance(obj, HasTraits):
                    obj.on_trait_change(binding.update_value, extended_name)

            element = self.element
            delegate_name = '_' + trait_name + '_delegate'
            element.add_trait(delegate_name, binding)
            element.add_trait(trait_name, DelegatesTo(delegate_name, 'value'))
            element.trait_added = trait_name

        self._binders.append(binder)
        self.bindings.append(binding)
    
    def add_delegate(self, trait_name, obj, obj_trait_name):
        validate_trait = self._valid_intercept(trait_name)
        delegate = Delegate(validate_trait=validate_trait, obj=obj,
                            trait_name=obj_trait_name)

        def binder():
            obj.on_trait_change(delegate.update_value, obj_trait_name)
            element = self.element
            delegate_name = '_' + trait_name + '_delegate'
            element.add_trait(delegate_name, delegate)
            element.add_trait(trait_name, DelegatesTo(delegate_name, 'value'))
            element.trait_added = trait_name
        
        self._binders.append(binder)
        self.delegates.append(delegate)
    
    def bind(self):
        # The binder closures are meant for one time use. We free them
        # so that the objects referenced in the closure can be freed.
        for binder in self._binders:
            binder()
        del self._binders

    def _valid_intercept(self, trait_name):
        """ Raises an error if the trait_name on element does not exist
        or is not suitable for intercepting. Returns a clone of the
        trait when successful.

        """
        element = self.element
        trait = element.trait(trait_name)
        if trait is None:
            msg = '`%s` is not trait on the %s view element.'
            raise AttributeError(msg % (trait_name, type(element).__name__))
        elif trait.type == 'property':
            msg = 'Cannot intercept `%s` trait, which is a Property.'
            raise TypeError(msg % trait_name)
        elif trait.type == 'event':
            msg = 'Cannot intercept `%s` trait, which is an Event.'
            raise TypeError(msg % trait_name)
        return trait()


