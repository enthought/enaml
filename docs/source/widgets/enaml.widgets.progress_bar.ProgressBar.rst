ProgressBar
======================================

.. currentmodule:: enaml.widgets.progress_bar

.. autoclass:: ProgressBar


Sample
--------

========= ======================================== ========================================= ===========================================
 System               Wx                                  Qt                                    Enaml
========= ======================================== ========================================= ===========================================
Windows   .. image:: ../images/wx/progress_bar.png .. image:: ../images/qt/progress_bar.png  .. include:: ../examples/progress_bar.enaml
                                                                                                :literal:
========= ======================================== ========================================= ===========================================

Backends
--------

Qt
^^

.. inheritance-diagram::
    enaml.widgets.qt.qt_progress_bar.QtProgressBar
    :parts: 1

.. autoclass:: enaml.widgets.qt.qt_progress_bar.QtProgressBar

Wx
^^

.. inheritance-diagram::
    enaml.widgets.wx.wx_progress_bar.WXProgressBar
    :parts: 1

.. autoclass:: enaml.widgets.wx.wx_progress_bar.WXProgressBar
