from .i_toggle_element import IToggleElement


class IRadioButton(IToggleElement):
    """ A radio button widget derived from IToggleElement 
    
    Use a radio button to toggle the value of a boolean field.
    For a group of radio buttons with the same widget parent, 
    only one radio button may be selected at a time. This makes 
    groups of radio buttons useful for selecting amongst a discrete
    set of values.

    See Also
    --------
    IToggleElement
    
    """
    pass

