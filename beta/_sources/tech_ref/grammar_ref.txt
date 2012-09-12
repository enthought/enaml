.. _grammar-ref:

|Enaml| Grammar Reference
===============================================================================

.. warning:: This documentation is not current and does not reflect the way
    Enaml currently works.

Five operators have special meaning in |Enaml| syntax: :ref:`assignment<def-assignment-opr>`, :ref:`delegation<delegation-opr>`, :ref:`subscription<subscription-opr>`, :ref:`update<update-opr>` and :ref:`notification<notification-opr>`

.. _def-assignment-opr:

"\=" Default Assignment Operator
-------------------------------------------------------------------------------
Use when you want to initialize the left hand side only once. Supports full Python expression syntax on right hand side.


.. _delegation-opr:

":=" Delegation Operator
-------------------------------------------------------------------------------
Use when you want a bidirectional sync between a variable/ui-element on left hand side and an assignable expression on right hand side. Supports 'assignable' expressions on the right hand side. Assignable expressions are expressions that can be used on left hand side of Python = operator. getattr is also supported as a special case and is set to be equivalent to attribute access expression.

.. _subscription-opr:

"<<" Subscription Operator
-------------------------------------------------------------------------------
Use when you want a variable/ui-element on left hand side to subscribe to the external world. Supports full Python expression syntax on right hand side.

.. _update-opr:

">>" Update Operator
-------------------------------------------------------------------------------
Use when you want to notify the external world about any changes in a variable/ui-element. Supports 'assignable' expressions on the right hand side. Assignable expressions are expressions that can be used on left hand side of Python = operator. getattr is also supported as a special case and is set to be equivalent to attribute access expression.

.. _notification-opr:

"::" Notification Operator
-------------------------------------------------------------------------------
Use when you just want to execute multiple statements whenever a variable/ui-element changes. '::' supports full Python grammar except: 'def', 'class', 'lambda', 'return', and 'yield' on right hand side.
