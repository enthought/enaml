from .qt_api import QtGui

from traits.api import implements

from .qt_control import QtControl

from ..spin_box import ISpinBoxImpl


class QtSpinBox(QtControl):
    """ A Qt implementation of SpinBox.

    See Also
    --------
    SpinBox

    """
    implements(ISpinBoxImpl)

    def create_widget(self):
        """ Creates the underlying custom spin control.

        """
        self.widget = QtGui.QSpinBox(self.parent_widget())

    def initialize_widget(self):
        """ Intializes the widget with the attributes of this instance.

        """
        parent = self.parent
        self.set_spin_low(parent.low)
        self.set_spin_high(parent.high)
        self.set_spin_step(parent.step)
        self.set_spin_prefix(parent.prefix)
        self.set_spin_suffix(parent.suffix)
        self.set_spin_special_value_text(parent.special_value_text)
        self.set_spin_to_string(parent.to_string)
        self.set_spin_from_string(parent.from_string)
        self.set_spin_wrap(parent.wrap)
        self.set_spin_value(parent.value)
        self.bind()

    def parent_value_changed(self, value):
        """ The change handler for the 'value' attribute. Not meant
        for public consumption.

        """
        self.set_spin_value(value)

    def parent_low_changed(self, low):
        """ The change handler for the 'low' attribute. Not meant
        for public consumption.

        """
        self.set_spin_low(low)

    def parent_high_changed(self, high):
        """ The change handler for the 'high' attribute. Not meant
        for public consumption.
        
        """
        self.set_spin_high(high)
    
    def parent_step_changed(self, step):
        """ The change handler for the 'step' attribute. Not meant
        for public consumption.
        
        """
        self.set_spin_step(step)
    
    def parent_prefix_changed(self, prefix):
        """ The change handler for the 'prefix' attribute. Not meant
        for public consumption.
        
        """
        self.set_spin_prefix(prefix)
    
    def parent_suffix_changed(self, suffix):
        """ The change handler for the 'suffix' attribute. Not meant
        for public consumption.

        """
        self.set_spin_suffix(suffix)
    
    def parent_special_value_text_changed(self, text):
        """ The change handler for the 'special_value_text' attribute.
        Not meant for public consumption.
        
        """
        self.set_spin_special_value_text(text)
    
    def parent_to_string_changed(self, to_string):
        """ The change handler for the 'to_string' attribute. Not meant
        for public consumption.
        
        """
        self.set_spin_to_string(to_string)
    
    def parent_from_string_changed(self, from_string):
        """ The change handler for the 'from_string' attribute. Not meant 
        for public consumption.
        
        """
        self.set_spin_from_string(from_string)
    
    def parent_wrap_changed(self, wrap):
        """ The change handler for the 'wrap' attribute. Not meant for
        public consumption.
        
        """
        self.set_spin_wrap(wrap)

    #---------------------------------------------------------------------------
    # Implementation
    #---------------------------------------------------------------------------
    def bind(self):
        """ Binds the event handlers for the spin control.

        """
        self.widget.valueChanged.connect(self.on_value_changed)

    def on_value_changed(self):
        """ The event handler for the widget's spin event. Not meant
        for public consumption.

        """
        self.parent.value = self.widget.value()

    def set_spin_value(self, value):
        """ Updates the widget with the given value. Not meant for 
        public consumption.

        """
        self.widget.setValue(value)

    def set_spin_low(self, low):
        """ Updates the low limit of the spin box. Not meant for 
        public consumption.

        """
        self.widget.setMinimum(low)
    
    def set_spin_high(self, high):
        """ Updates the high limit of the spin box. Not meant for 
        public consumption.

        """
        self.widget.setMaximum(high)
    
    def set_spin_step(self, step):
        """ Updates the step of the spin box. Not meant for public
        consumption.

        """
        self.widget.setSingleStep(step)
    
    def set_spin_prefix(self, prefix):
        """ Updates the prefix of the spin box. Not meant for public
        consumption.

        """
        self.widget.setPrefix(prefix)

    def set_spin_suffix(self, suffix):
        """ Updates the suffix of the spin box. Not meant for public
        consumption.

        """
        self.widget.setSuffix(suffix)

    def set_spin_special_value_text(self, text):
        """ Updates the special value text of the spin box. Not meant
        for public consumption.

        """
        self.widget.setSpecialValueText(text)
    
    def set_spin_to_string(self, to_string):
        """ Updates the to_string function of the spin box. Not meant
        for public consumption.

        """
        def compute_text(value):
            """ Override QSpinBox::textFromValue by wrapping `to_string`
            in a try/except block.
            
            """
            parent = self.parent
            try:
                value = to_string(value)
            except ValueError:
                value = parent.value
            finally:
                return value
        
        self.widget.textFromValue = compute_text
    
    def set_spin_from_string(self, from_string):
        """ Updates the from_string function of the spin box. Not meant
        for public consumption.

        """
        def compute_value(text):
            """ Override QSpinBox::valueFromText by wrapping `from_string`
            in a try/except block.
            
            """
            parent = self.parent
            
            # If 'len(parent.suffix) == 0', go to the end of the string: [-1].
            suffix_len = -len(parent.suffix) or -1
            entered = text[len(parent.prefix):suffix_len]
            
            try:
                result = from_string(entered)
            except ValueError:
                result = parent.value
            finally:
                return result
        
        self.widget.valueFromText = compute_value
    
    def set_spin_wrap(self, wrap):
        """ Updates the wrap value of the spin box. Not meant for public
        consumption.

        """
        self.widget.setWrapping(wrap)

