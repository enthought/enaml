#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------

from traits.api import HasTraits, Range, Float, Long, on_trait_change


class RangeDemo(HasTraits):
    """Demonstrate numeric text fields with restricted ranges.

    The Range trait attributes are not inspected by enaml.  It is up to the
    author of the .enaml file to match the UI attributes to the Trait
    attributes.
    """

    i = Range(low=0)

    digit = Range(low=0, high=9)

    bigint = Long(1000L)

    x = Range(low=0.0)

    y = Range(low=0.0, high=10.0, value=5)

    z = Range(low=0.0, high=10.0, value=5)

    beta_min = Range(high=0.0, value=-1.0)

    beta_max = Range(low=0.0, value=1.0)

    beta = Range(low='beta_min', high='beta_max', value=0.0)

    h = Range(low=0, high=255)
 
    def _anytrait_changed(self):
        """Prints all the trait values whenever a trait changes."""
        for name in self.editable_traits():
            print "{name} = {value}  ".format(name=name, value=repr(getattr(self, name))),
        print


def enaml_demo():
    import enaml
    with enaml.imports():
        from range_demo_view import RangeDemoView

    demo = RangeDemo()

    view = RangeDemoView(demo)
    view.show()


if __name__ == '__main__':
    enaml_demo()
