#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
""" Driver for the sine plot example.

The window will show a Chaco plot on the left with sin(x) and cos(x) 
functions. The right side of the window will be a Form showing sliders 
that control the phase, amplitude, and angular frequency of the sinusoidal 
functions. The plot will update whenever the slider values change.

This demo requires numpy and Chaco.

"""
import numpy as np

from traits.api import HasTraits, Array, Float, Property

import enaml


class SineModel(HasTraits):
    #: The phase of the sine wave.
    phase = Float()

    #: The amplitude of the sine wave.
    amplitude = Float(1.0)

    #: The angular frequency of the sine wave.
    w = Float(1.0)

    #: The data.
    x = Array()
    def _x_default(self):
        return np.linspace(-6*np.pi, 6*np.pi, 301)

    y_sin = Property(Array, depends_on=['phase', 'amplitude', 'w'])
    def _get_y_sin(self):
        return self.amplitude * np.sin(self.w * self.x + self.phase)

    y_cos = Property(Array, depends_on=['phase', 'amplitude', 'w'])
    def _get_y_cos(self):
        return self.amplitude * np.cos(self.w * self.x + self.phase)


def main():
    from simple_plot import SimplePlot
    SimplePlot.activate()

    with enaml.imports():
        from sine_plot import Main

    model = SineModel()
    window = Main(model=model)
    window.show()


if __name__ == '__main__':
    main()

