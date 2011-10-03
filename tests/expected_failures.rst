======================
Expected Test Failures
======================

October 3rd, 2011

9 test are currently expected fail.
1 test is skipped.

Introduction
============

The failed tests indicate unexpected behavior. This includes mismatches
between Enaml widgets and their toolkit implementations, and differences
between the Qt and wxPython toolkit backends.

Failures
========

enaml.widgets.calendar.Calendar
-------------------------------
4 failures (2 wxPython, 2 Qt)

* Calendar.date is not constrained by the minimum_date and maximum_date values,
  at least not for the initial values.

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

Qt will step up to 5, but wxPython wraps to 0. The test expects Qt's behavior.


enaml.widgets.field.Field
-------------------------
3 failures (1 wxPython, 2 Qt)

* Qt doesn’t fire max_length_reached Event.
* The text_changed and text_edited Events are always fired together.
