enaml core
==========

The core implementation provides all the necessary machinery to create a
thin layer over backend widgets and produce the traits View objects.

:mod:`enums` Module
-------------------

.. inheritance-diagram:: enaml.enums.Enum
    :parts: 1

.. automodule:: enaml.enums

:mod:`converters` Module
------------------------

.. inheritance-diagram:: enaml.converters
    :parts: 1

.. automodule:: enaml.converters

:mod:`expressions` Module
-------------------------

.. inheritance-diagram:: enaml.core.expressions.ExpressionScope
    :parts: 1

.. inheritance-diagram:: enaml.core.expressions.TraitAttributeNotifier
    :parts: 1

.. inheritance-diagram:: enaml.core.expressions.AbstractExpression
                         enaml.core.expressions.SimpleExpression
			 enaml.core.expressions.SubscriptionExpression
			 enaml.core.expressions.NotifyingExpression
			 enaml.core.expressions.DelegatingExpression
    :parts: 1

.. automodule:: enaml.core.expressions
    :special-members:
    :no-undoc-members:

:mod:`exceptions` Module
-------------------------

.. inheritance-diagram:: enaml.exceptions
    :parts: 1

.. automodule:: enaml.exceptions

:mod:`toolkit` Module
---------------------

.. automodule:: enaml.core.toolkit

:mod:`import_hooks` Module
--------------------------

.. automodule:: enaml.core.import_hooks
