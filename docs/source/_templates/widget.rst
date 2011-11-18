{{ objname }}
{{ underline }}

.. currentmodule:: {{ module }}

.. autoclass:: {{ objname }}

{ # todo: properly convert the name from camel case to underscore separated
  lower case name # }

Backends
--------


Qt
^^

.. inheritance-diagram::
    enaml.widgets.qt.qt_{{ objname|lower }}.Qt{{ objname }}
    :parts: 1

.. autoclass:: enaml.widgets.qt.qt_{{ objname|lower }}.Qt{{ objname }}

Wx
^^

.. inheritance-diagram::
    enaml.widgets.wx.wx_{{ objname|lower }}.WX{{ objname }}
    :parts: 1

.. autoclass:: enaml.widgets.wx.wx_{{ objname|lower }}.WX{{ objname }}

