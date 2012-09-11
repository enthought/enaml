enaml.core
==========

The :py:mod:`enaml.core` package contains all of the core functionality of the
Enaml toolkit.


:mod:`import_hooks` Module
--------------------------

.. automodule:: enaml.core.import_hooks


:mod:`expressions` Module
-------------------------

.. inheritance-diagram:: enaml.core.expressions.ExecutionScope
    :parts: 1

.. inheritance-diagram:: enaml.core.expressions.NonlocalScope
    :parts: 1

.. inheritance-diagram:: enaml.core.expressions.AbstractExpression
                         enaml.core.expressions.SimpleExpression
                         enaml.core.expressions.NotificationExpression
                         enaml.core.expressions.UpdateExpression
                         enaml.core.expressions.SubscriptionExpression
                         enaml.core.expressions.DelegationExpression
    :parts: 1

.. automodule:: enaml.core.expressions
    :special-members:
    :no-undoc-members:


:mod:`item_model` Module
---------------------------------

.. autoclass:: enaml.core.item_model.AbstractItemModel

.. autoclass:: enaml.core.item_model.AbstractTableModel

.. autoclass:: enaml.core.item_model.AbstractListModel

.. autoclass:: enaml.core.item_model.ModelIndex


:mod:`enaml_ast` Module
-----------------------

.. inheritance-diagram:: enaml.core.enaml_ast
    :parts: 1

.. automodule:: enaml.core.enaml_ast


:mod:`lexer` Module
-------------------

.. currentmodule:: enaml.core.lexer

.. autoclass:: EnamlLexer
    :no-members:
    :members: __init__, input, token, dedent, indent,
        make_token_stream, create_strings,
        annotate_indentation_state, synthesize_indentation_tokens,
        add_endmarker

:mod:`parser` Module
--------------------

.. automodule:: enaml.core.parser

:mod:`enaml_compiler` Module
----------------------------

.. automodule:: enaml.core.enaml_compiler
