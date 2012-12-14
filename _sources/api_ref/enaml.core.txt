enaml.core
==========

The :py:mod:`enaml.core` package contains all of Enaml's core language functionality.


:mod:`abstract_expressions` Module
----------------------------------

.. automodule:: enaml.core.abstract_expressions


:mod:`code_tracing` Module
--------------------------

.. automodule:: enaml.core.code_tracing


:mod:`compiler_helpers` Module
------------------------------

.. automodule:: enaml.core.compiler_helpers


:mod:`declarative` Module
-------------------------
.. automodule:: enaml.core.declarative


:mod:`enaml_ast` Module
-----------------------

.. inheritance-diagram:: enaml.core.enaml_ast
    :parts: 1

.. automodule:: enaml.core.enaml_ast


:mod:`enaml_compiler` Module
----------------------------

.. automodule:: enaml.core.enaml_compiler


:mod:`enaml_def` Module
-----------------------

.. automodule:: enaml.core.enaml_def


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


:mod:`funchelper` Module
------------------------

.. automodule:: enaml.core.funchelper


:mod:`import_hooks` Module
--------------------------

.. automodule:: enaml.core.import_hooks


:mod:`include` Module
---------------------

.. automodule:: enaml.core.include


:mod:`lexer` Module
-------------------

.. currentmodule:: enaml.core.lexer

.. autoclass:: EnamlLexer
    :no-members:
    :members: __init__, input, token, dedent, indent,
        make_token_stream, create_strings,
        annotate_indentation_state, synthesize_indentation_tokens,
        add_endmarker


:mod:`messenger` Module
-----------------------

.. automodule:: enaml.core.messenger


:mod:`object` Module
--------------------
.. automodule:: enaml.core.object


:mod:`operator_context` Module
------------------------------

.. automodule:: enaml.core.operator_context


:mod:`operators` Module
-----------------------
.. automodule:: enaml.core.operators


:mod:`parser` Module
--------------------

.. automodule:: enaml.core.parser


:mod:`trait_types` Module
-------------------------

.. automodule:: enaml.core.trait_types

