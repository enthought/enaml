#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from ...core.constructor import Constructor


def importer(module_path, name):
    def _importer():
        mod = __import__(module_path, fromlist=[name])
        try:
            res = getattr(mod, name)
        except AttributeError:
            raise ImportError('Cannot import name %s' % name)
        return res
    return _importer


def constructor(base_path):
    """ A factory function which understands our name mangling and will
    create a constructor instance. Returns tuple of (name, ctor) where
    name is a string that can be used by toolkit to refer to the ctor
    in the enaml source code.

    """
    c_module_path = 'enaml.widgets.' + base_path
    c_name = ''.join(part.capitalize() for part in base_path.split('_'))

    t_module_path = 'enaml.widgets.wx.' + 'wx_' + base_path
    t_name = 'WX' + c_name

    component_loader = importer(c_module_path, c_name)
    abstract_loader = importer(t_module_path, t_name)

    ctor = Constructor(component_loader, abstract_loader)

    return c_name, ctor


WX_CONSTRUCTORS = dict((
    constructor('main_window'),
    constructor('dialog'),
    constructor('container'),
    constructor('calendar'),
    constructor('check_box'),
    constructor('combo_box'),
    constructor('field'),
    constructor('html'),
    constructor('image'),
    constructor('label'),
    constructor('push_button'),
    constructor('radio_button'),
    constructor('slider'),
    constructor('spin_box'),
    constructor('traitsui_item'),
    constructor('enable_canvas'),
    constructor('table_view'),
    constructor('date_edit'),
    constructor('datetime_edit'),
    constructor('form'),
    constructor('group_box'),
    constructor('progress_bar'),
    constructor('scroll_area'),
    constructor('tab_group'),
    constructor('tab'),
    constructor('splitter'),
    constructor('float_slider'),
    constructor('menu_bar'),
    constructor('menu'),
    constructor('action'),
))

