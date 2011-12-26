.. _tut_python_code

Python code and convenience functions in |Enaml|
===============================================================================

In this tutorial, we introduce a "magic" component for quickstart and debugging
purposes, and we show how to insert Python code blocks into an |Enaml|
file. This is useful for setting up variables and substitutions in the GUI
definition and as a convenience for self-contained GUI applications. (It is in
fact a great convenience for tutorials, examples, and demonstrations.)


The MainWindow component
-------------------------------------------------------------------------------

|Enaml| comes with a convenient utility that runs from the command-line:

::

 enaml-run <enaml_filename.enaml>

``enaml-run`` looks for a component called "``MainWindow``" in
*enaml_filename.enaml* and runs it as a stand-alone application. MainWindow
can also be called and executed from within Python code as usual. This is just
a convenience that allows you to try out your user interface without running
all of the other code that may go with it in the end application.
