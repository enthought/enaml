==============================
Enaml is not a Markup Language
==============================

Enaml is a framework for writing declarative user interfaces in Python.
It provides a Yaml-ish/Pythonic syntax language for declaring a ui
that binds and reacts to changes in the user's models. Code can freely 
call back and forth between Python and Enaml.

Enaml is heavily inspired by Qt's QML system, but Enaml uses native
widgets (as opposed to drawing on a 2D canvas) and is toolkit independent.
Currently supported/in-development toolkits include Wx and Qt4 via PySide.

Enaml is extensible and makes it extremely easy for the user to define
their own widgets, override existing widgets, create a new backend toolkit,
or even hook the runtime to apply their own expression dependency behavior.
Indeed, about the only thing not hookable is the Enaml langauge syntax
itself.

The enamldoc package provides a Sphinx extension for documenting Enaml object
types "enaml_decl" and "enaml_defn".

Prerequisites
-------------
* Python >= 2.6 (not Python 3)
* Traits
* Casuarius (https://github.com/enthought/casuarius)
* PySide (only if using the Qt backend)
* wxPython (only if using the wx backend)
* PLY (Python Lex-Yacc), for parsing *.enaml* files
* Sphinx (only if building the docs)
