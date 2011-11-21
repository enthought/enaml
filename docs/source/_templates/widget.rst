{{ objname }}
{{ underline }}

.. currentmodule:: {{ module }}

.. autoclass:: {{ objname }}


Backends
--------

Qt
^^

.. inheritance-diagram::
    {{ module|replace('widgets.', 'widgets.qt.qt_') }}.Qt{{ objname }}
    :parts: 1

.. autoclass:: {{ module|replace('widgets.', 'widgets.qt.qt_') }}.Qt{{ objname }}

Wx
^^

.. inheritance-diagram::
    {{ module|replace('widgets.', 'widgets.wx.wx_') }}.WX{{ objname }}
    :parts: 1

.. autoclass:: {{ module|replace('widgets.', 'widgets.wx.wx_') }}.WX{{ objname }}

