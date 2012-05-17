.. _tutorial_more_widgets:

More on |Enaml| Widgets
===============================================================================

In this tutorial, we take a closer look at some of the widgets available for
building GUI's in |Enaml| by building a "working" progress bar. We'll introduce
some new attributes including the ``id`` tag and two new |Enaml| operators: the
subscription operator ``<<`` and the notification operator ``::`` along with
some component-specific attributes.

Let's start with a code snippet from :download:`progress_bar.enaml
<../../../examples/components/progress_bar.enaml>`:

::

    enamldef Main(MainWindow):
        attr model: ProgressModel = ProgressModel()
        title = 'Progress Bar'
        Container:
            constraints = [
                vbox(progress,
                    hbox(spacer, label, spacer), 
                    hbox(spacer, work_button, spacer),
                    spacer),
                align('h_center', progress, label, work_button),
            ]
            ProgressBar:
                id: progress
                value := model.units_done
                maximum := model.work_units
            Label:
                id: label
                text << '{0}% ({1}/{2})'.format(progress.percentage, progress.value, progress.maximum)
            PushButton:
                id: work_button
                text << "Do Some Work" if progress.percentage < 100 else "Reset"
                clicked :: 
                    if progress.percentage < 100:
                        model.do_work()
                    else:
                        model.reset()


We're setting up a view which builds on a top-level ``MainWindow``. The view
has an attribute ``model`` which must be an instance of ``ProgressModel``,
and by default it is initialized to an instance of the class.  The window
has a ``Container`` which itself contains three widgets: a ``ProgressBar``, a
``Label``, and a ``PushButton``. (In the :ref:`tech-ref` you can find a list and
descriptions of widgets and components from the :ref:`built-ins <built-ins-ref>`
and :ref:`standard library <std-library-ref>`.)

In this example, we see some things we have not seen before:
    * the ProgressBar, Label and PushButton have ``id`` tags.
    * the text attributes of the Label and PushButton both use the subscription
      operator ``<<``
    * the PushButton's ``clicked`` event uses the notification operator ``::``
    * the Container object has a ``constraints`` attribute

``id`` Tags
-------------------------------------------------------------------------------

|Enaml| uses a special attribute called an ``id`` tag to let you refer to a
component or widget from elsewhere in the declaration. Note that no quotation
marks are necessary. Because of the line ``id: progress`` under
``ProgressBar:`` we can refer to this component as ``progress`` in code blocks
of similar *scope*. (We will have a more detailed discussion of scope later.)
``progress`` has two other attributes whose values we delegate with the ``:=``
operator.

Subscription Operator ``<<``
-------------------------------------------------------------------------------

The **subscription operator** ``<<`` is an |Enaml|-specific operator that makes
the object on the left-hand side depend on the value of the Python-valid
expression on the right-hand side of the operator. If there are variables in
the expression on the right-hand side, then |Enaml| registers dependencies for
each, and when any of the variable objects in the expression changes, the
object on the left-hand side will be recomputed.

::

    text << '{0}% ({1}/{2})'.format(progress.percentage, progress.value, progress.maximum)

The ``text`` attribute of the ``Label`` object in our example is *subscribed*
to a formatted string, with dependencies on ``progress.percentage``,
``progress.value``, and ``progress.maximum``.

Enaml's dependency analysis is quite sophisticated, and will connect
dependencies across multiple attribute lookups, and even into list
comprehensions, if-else expressions and other complex Python constructs.

::

    text << "Do Some Work" if progress.percentage < 100 else "Reset"

The ``work_button`` widget also has a subscribed text attribute; in this case it
is a Python ``if`` statement dependent on the value of ``progress.percentage``.

Notification Operators ``::`` and ``>>``
-------------------------------------------------------------------------------

The **notification operator** ``::`` is different from the other |Enaml|
operators in that it is followed by a block of Python code, rather than a Python
expression.  Whenever the attribute or event on the left-hand side of the
notification operator changes, the block of code will be executed.

::

    clicked :: 
        if progress.percentage < 100:
            model.do_work()
        else:
            model.reset()

In our example, changes to the ``clicked`` attribute of ``work_button`` will
cause the methods ``model.do_work()`` or ``model_reset()`` to be called
depending on the value of ``progress.percentage`` at the time that the change
happens.

It is worth mentioning at this point that there is one remaining |Enaml|
operator, ``>>`` which pushes a value onto another when it changes.  The
right-hand side of this operator must be a simple attribute expression which
will get set with the new value of the left-hand side.

For example, if our model had an object with a ``percentage`` trait, we could
have the ``ProgressBar`` use the ``>>`` operator to update it.

::

    ProgressBar:
        id: progress
        progress >> model.progress

This is a short-hand for the equivalent::

    ProgressBar:
        id: progress
        progress ::
            model.progress = progress

Similarly, the delegation operator ``:=`` as used like this::

    ProgressBar:
        id: progress
        value := model.units_done

is equivalent to::

    ProgressBar:
        id: progress
        value << model.units_done
        value >> model.units_done


Constraints
-------------------------------------------------------------------------------

One of the primary motivations for the development of the Enaml toolkit was to
allow greater control over the appearance and layout of user interfaces built
on top of Traits.  Until this point we have been relying on the default layouts
provided by container widgets like ``Container`` and ``Form``, but we have the
option to override these so we can specify layout more precisely.

By default the ``Container`` widget lays out its child widgets in a vertical
stack, with each widget stretched horizontally to the width of the container.
In the progress bar example, we have defined a replacement set of constraints
by setting a value on the ``constraints`` attribute of the Container.

::

    constraints = [
        vbox(progress,
            hbox(spacer, label, spacer), 
            hbox(spacer, work_button, spacer),
            spacer),
        align('h_center', progress, label, work_button),
    ]

This layout is hopfully fairly clear:: the children of the container should be
layed out vertically in a box, with the progress bar above the label which is
in turn above the work_button.  At the bottom is a spacer, which provides an
expanding amount of space, meaning that the other items in the vbox will not
expand.  Similarly, the label and work_button are layed out inside horizontal
boxes with spacers on either side, so they will not expand horizontally beyond
their natural width.

Finally we constrain the three widgets so that they are aligned on their
horizontal centers, meaning that the vertical stack of widgets will align to
the center of the container.

The objects ``vbox``, ``hbox``, ``align`` and ``spacer`` are conveniences that
simplify layout.  They all evaluate down to a series of linear inequalities
which are solved by the `casuarius <https://github.enthought.com/casuarius>`_
linear constraint solver.

We can add additional constraints via inequalities directly, if we want.  For
example, if we would like to make sure that the progress bar is at least 500
pixels wide, we could add that an inequality to the constraints::

    constraints = [
        vbox(progress,
            hbox(spacer, label, spacer), 
            hbox(spacer, work_button, spacer),
            spacer),
        align('h_center', progress, label, work_button),
        progress.width >= 500,
    ]

For constraints like this which involve only one component, it is sometimes
clearer to add them to the constraints attribute of the widget itself::

    ProgressBar:
        id: progress
        constraints = [width >= 500,]
        value := model.units_done
        maximum := model.work_units

Linear equalities and inequalities are also permitted in the set of constraints,
so we could insist that the progress bar be at least twice the width of the
label::

    constraints = [
        vbox(progress,
            hbox(spacer, label, spacer), 
            hbox(spacer, work_button, spacer),
            spacer),
        align('h_center', progress, label, work_button),
        progress.width >= 2*label.width,
    ]

::

 :: python ::

 import random
 from traits.api import HasTraits, Int

 class Model(HasTraits):
     """ Model a process that does some work on command.
     """
     # The total units of work to do.
     work_units = Int(1000)

     # The number of units done.
     units_done = Int(0)

     def do_work(self):
         """ Do a random amount of work.
         """
         nunits = random.randint(10, 100)
         nunits = min(nunits, self.work_units - self.units_done)
         self.units_done += nunits

     def reset(self):
         """ Reset the work done back to 0.
         """
         self.units_done = 0
 :: end ::

Note that logically, this section of Python code should go *before* the veiw
declaration, but |Enaml| files are executed "all at once", and the order of
declaration does not matter [#]_. Within the Python code tags, of course, the normal
rules of Python parsing and execution apply.

With a separate piece of Python code, we set up the main() function for
running from the command line:

::

    :: python ::

    # A 'main' function is special cased as an entry point by the enaml-run script
    def main():
        model = Model()
        window = ModelView(model)
        window.show()

    :: end ::

Execute from the command line with

::

 $ enaml-run progress_bar.enaml 

.. image:: images/progress_bar_simple.png

.. [#] Technically, the right-hand side of an |Enaml| operator acts as a
   closure which has access to all of the identifiers declared in the block.
