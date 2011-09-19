import os

from traits.api import HasStrictTraits, Dict, Str, Callable, Any, Instance

from .constructors import IToolkitConstructor
from .style_sheet import StyleSheet
from .util.trait_types import SubClass


class Toolkit(HasStrictTraits):
    """ A simple class that handles toolkit related functionality.

    Attributes
    ----------
    items : Dict(Str, SubClass(IToolkitConstructor))
        A dictionary which maps type names in the Enaml source code
        to toolkit constructor classes for that name. This dict
        can be modified to make new widgets available to the Enaml
        source code.

    prime : Callable
        A callable which initializes the toolkit's event loop. This
        will be called before any toolkit widgets are created. Most
        toolkits will create the application object in this function.
        The return value of this callable is passed to the 'start'
        callable when the event loop should be started.

    start : Callable
        This is called at the end of the ui building process, after
        the 'show' method on the view has been called. This function
        should make sure the event loop for the toolkit is started.
        It should take one argument, which is the return value from
        the 'prime' method.

    app : Any
        The return value of the 'prime' callable is stored in this
        attribute. This will usually be the toolkit's application
        object.

    style_sheet : SubClass(StyleSheet)
        A default style sheet class for this toolkit.

    utils : Dict(Str, Callable)
        Callables used to construct simple ui elements in the RHS of a
        delegate expression. Unlike 'items', these are not independent
        components in Enaml source code.

    Methods
    -------
    create_ctor(name):
        Creates the constructor instance for the given name, or raises
        an error if no constructor is defined for that name.

    prime_event_loop()
        Called before any ui tree building takes place in order to 
        prime the toolkit's event loop.

    start_event_loop()
        Called at the end of the View's 'show' method to start the 
        toolkit's event loop.
    
    default_style_sheet()
        Returns the default style sheet class for this toolkit.

    """
    items = Dict(Str, SubClass(IToolkitConstructor))

    prime = Callable

    start = Callable

    app = Any

    style_sheet = Instance(StyleSheet)
    
    utils = Dict(Str, Callable)

    def __init__(self, items, prime, start, style_sheet, utils):
        super(Toolkit, self).__init__(items=items, prime=prime, start=start,
                                      style_sheet=style_sheet, utils=utils)

    def create_ctor(self, name):
        """ Creates the constructor instance for the given name, or 
        raises an error if no constructor is defined for that name.

        """
        try:
            ctor_cls = self.items[name]
        except KeyError:
            msg = 'Toolkit does not support the %s item.' % name
            raise ValueError(msg)
        return ctor_cls(type_name=name)
    
    def prime_event_loop(self):
        """ Called before any ui tree building takes place in order to 
        prime the toolkit's event loop. 
        
        """
        self.app = self.prime()
    
    def start_event_loop(self):
        """ Called at the end of the View's 'show' method to start the 
        toolkit's event loop.
        
        """
        self.start(self.app)
    
    def default_style_sheet(self):
        """ Returns the default style sheet class for this toolkit.

        """
        return self.style_sheet


def default_toolkit():
    """ Creates an returns the default toolkit object based on
    the user's current ETS_TOOLKIT environment variables.

    """
    toolkit = os.environ.get('ETS_TOOLKIT', 'wx').lower()
    
    if toolkit == 'wx':
        return wx_toolkit()
        
    if toolkit == 'qt' or toolkit == 'qt4':
        return qt_toolkit()
    
    raise ValueError('Invalid Toolkit: %s' % toolkit)


def wx_toolkit():
    """ Creates and return a toolkit object for the wx backend.

    """
    from .util.guisupport import get_app_wx, start_event_loop_wx
    from .widgets.wx import constructors as ctors
    from .widgets.wx import dialogs
    from .widgets.wx.styling import WX_STYLE_SHEET

    items = {
        'Panel': ctors.WXPanelCtor,
        'Window': ctors.WXWindowCtor,
        'Dialog': ctors.WXDialogCtor,
        'Form': ctors.WXFormCtor,
        'Group': ctors.WXGroupCtor,
        'VGroup': ctors.WXVGroupCtor,
        'HGroup': ctors.WXHGroupCtor,
        'StackedGroup': ctors.WXStackedGroupCtor,
        'TabGroup': ctors.WXTabGroupCtor,
        'GroupBox': ctors.WXGroupBoxCtor,
        'Calendar': ctors.WXCalendarCtor,
        'CheckBox': ctors.WXCheckBoxCtor,
        'ComboBox': ctors.WXComboBoxCtor,
        'Field': ctors.WXFieldCtor,
        'Html': ctors.WXHtmlCtor,
        'Image': ctors.WXImageCtor,
        'Label': ctors.WXLabelCtor,
        'PushButton': ctors.WXPushButtonCtor,
        'RadioButton': ctors.WXRadioButtonCtor,
        'Slider': ctors.WXSliderCtor,
        'SpinBox': ctors.WXSpinBoxCtor,
        'Spacer': ctors.WXSpacerCtor,
        'EnableCanvas': ctors.WXEnableCanvasCtor,
        'TraitsUIItem': ctors.WXTraitsUIItemCtor,
        'TableView': ctors.WXTableViewCtor,
        'CheckGroup': ctors.WXCheckGroupCtor,
    }

    utils = {
        'error': dialogs.error,
        'warning': dialogs.warning,
        'information': dialogs.information,
        'question': dialogs.question
    }

    return Toolkit(items=items, prime=get_app_wx, start=start_event_loop_wx,
                   style_sheet=WX_STYLE_SHEET, utils=utils)


def qt_toolkit():
    """ Creates and return a toolkit object for the PySide Qt backend.

    """
    from .util.guisupport import get_app_qt4, start_event_loop_qt4
    from .widgets.qt import constructors as ctors
    from .widgets.qt.styling import QT_STYLE_SHEET

    items = {
        'Panel': ctors.QtPanelCtor,
        'Window': ctors.QtWindowCtor,
        'Dialog': ctors.QtDialogCtor,
        'Group': ctors.QtGroupCtor,
        'VGroup': ctors.QtVGroupCtor,
        'HGroup': ctors.QtHGroupCtor,
        'Form': ctors.QtFormCtor,
        'StackedGroup': ctors.QtStackedGroupCtor,
        'TabGroup': ctors.QtTabGroupCtor,
        'Field': ctors.QtFieldCtor,
        'Label': ctors.QtLabelCtor,
        'TraitsUIItem': ctors.QtTraitsUIItemCtor,
        'Calendar': ctors.QtCalendarCtor,
        'CheckBox': ctors.QtCheckBoxCtor,
        'ComboBox': ctors.QtComboBoxCtor,
        'Html': ctors.QtHtmlCtor,
        'PushButton': ctors.QtPushButtonCtor,
        'RadioButton': ctors.QtRadioButtonCtor,
        'Slider': ctors.QtSliderCtor,
        'SpinBox': ctors.QtSpinBoxCtor,
        'EnableCanvas': ctors.QtEnableCanvasCtor,
        'TableView': ctors.QtTableViewCtor,
        'CheckGroup': ctors.QtCheckGroupCtor,
    }
    
    utils = {}

    return Toolkit(items=items, prime=get_app_qt4, start=start_event_loop_qt4,
        style_sheet=QT_STYLE_SHEET, utils=utils)
