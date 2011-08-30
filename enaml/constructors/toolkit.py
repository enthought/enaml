import os

    
def default_toolkit():

    toolkit = os.environ.get('ETS_TOOLKIT', 'wx').lower()
    
    if toolkit == 'wx':
        return wx_toolkit()
        
    if toolkit == 'qt' or toolkit == 'qt4':
        qt_api = os.environ.get('QT_API', 'pyside').lower()
        
        if api == 'pyside':
            return pyside_toolkit()
        
        if qt_api == 'pyqt' or qt_api == 'pyqt4':
            return pyqt_toolkit()
        
        raise ValueError('Invalid QT_API: %s' % qt_api)
    
    raise ValueError('Invalid Toolkit: %s' % toolkit)


def wx_toolkit():
    from . import wx_constructors as ctors
    return {
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
        'LineEdit': ctors.WXLineEditCtor,
        'PushButton': ctors.WXPushButtonCtor,
        'RadioButton': ctors.WXRadioButtonCtor,
        'Slider': ctors.WXSliderCtor,
        'SpinBox': ctors.WXSpinBoxCtor,
        'TraitsUIItem': ctors.WXTraitsUIItemCtor,
    }


def pyside_toolkit():
    raise NotImplementedError


def pyqt_toolkit():
    raise NotImplementedError

