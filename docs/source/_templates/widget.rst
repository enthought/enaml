{{ objname }}
{{ underline }}

.. currentmodule:: {{ module }}

.. autoclass:: {{ objname }}


Backends
--------

Qt
^^

.. inheritance-diagram::
    {{ module|replace('components.', 'backends.qt.qt_') }}.Qt{{ objname }}
    :parts: 1

.. autoclass:: {{ module|replace('components.', 'backends.qt.qt_') }}.Qt{{ objname }}

Wx
^^

.. inheritance-diagram::
    {{ module|replace('components.', 'backends.wx.wx_') }}.WX{{ objname }}
    :parts: 1

.. autoclass:: {{ module|replace('components.', 'backends.wx.wx_') }}.WX{{ objname }}

