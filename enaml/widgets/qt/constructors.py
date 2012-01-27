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


def shell_loader(base_path):
    """ Get the shell class loader for the given name.

    Parameters
    ----------
    base_path : str
        The lowercase-with-underscores name of the module containing the 
        shell class.

    Returns
    -------
    c_name : str
        The name of the shell class.

    shell_loader : callable
        The loader function for the shell class.

    """
    c_module_path = 'enaml.widgets.' + base_path
    c_name = ''.join(part.capitalize() for part in base_path.split('_'))
    shell_loader = importer(c_module_path, c_name)
    return c_name, shell_loader


def abstract_loader(c_name, base_path):
    """ Get the abstract class loader for the given name.

    Parameters
    ----------
    c_name : str
        The TitleCase class name of the shell class.

    base_path : str
        The lowercase-with-underscores name of the module containing the 
        shell class.

    Returns
    -------
    abstract_loader : callable
        The loader function for the abstract class.

    """
    t_module_path = 'enaml.widgets.qt.' + 'qt_' + base_path
    t_name = 'Qt' + c_name
    abstract_loader = importer(t_module_path, t_name)
    return abstract_loader


def constructor(base_path):
    """ A factory function which understands our name mangling and will
    create a constructor instance. Returns tuple of (name, ctor) where
    name is a string that can be used by toolkit to refer to the ctor
    in the enaml source code.

    """
    c_name, shell_ldr = shell_loader(base_path)
    abstract_ldr = abstract_loader(c_name, base_path)
    ctor = Constructor(shell_ldr, abstract_ldr)
    return c_name, ctor


base_sel_model = constructor('base_selection_model')[1]
row_sel_model = base_sel_model.clone(shell_loader('row_selection_model')[1])


QT_CONSTRUCTORS = dict((
    constructor('main_window'),
    constructor('container'),
    constructor('dialog'),
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
    constructor('text_editor'),
    constructor('list_view'),
    constructor('table_view'),
    constructor('tree_view'),
    constructor('date_edit'),
    constructor('datetime_edit'),
    constructor('form'),
    constructor('group_box'),
    constructor('scroll_area'),
    constructor('progress_bar'),
    constructor('tab_group'),
    constructor('tab'),
    constructor('splitter'),
    constructor('float_slider'),
    ('BaseSelectionModel', base_sel_model),
    ('RowSelectionModel', row_sel_model),
    constructor('menu_bar'),
    constructor('menu'),
    constructor('action'),
))

