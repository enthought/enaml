======================
Expected Test Failures
======================

October 5rd, 2011

5 test are currently expected fail.
2 test is skipped.

Introduction
============

The failed tests indicate unexpected behaviour. This includes mismatches
between Enaml widgets and their toolkit implementations, and differences
between the components based on the Qt and wxPython toolkit backends.

Failures
========

enaml.widgets.spin_box.SpinBox
------------------------------
2 failures (inconsistency between Qt and wxPython)

Given a spin box::

    SpinBox:
        min = 0
        max = 5
        step = 2
        value = 4
        wrap = True

Qt will step up to 5, but wxPython wraps to 0. The test expects Qt's behaviour.


enaml.widgets.field.Field
-------------------------
3 failures (1 wxPython, 2 Qt)

* Qt doesn't fire max_length_reached Event.
* The text_changed and text_edited Events are always fired together.

Skips
=====

Skipped test indicate that it is yet possible to verify some functionality
of individual toolkit based components. This is either because the is missing
test code or the specific toolkit based component does not provide that
functionality.

enaml.widgets.date_edit.DateEdit

Setting the date format in a wxPython based enaml component is not implemented
yet. This could be a ms windows peculiarity.

enaml.widgets.slider.Slider

It is not yet possible to find if the wxpython based slider widget (not the enaml
component) is in tracking mode. Tracking mode in the widget is controlled by
binding and unbinding the component to wxslider thunb tracking event. We
need a method to check if the callback function is bound to the singal
without firing the singal.
