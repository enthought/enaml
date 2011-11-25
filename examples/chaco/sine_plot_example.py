#!/usr/bin/env python
# -*- coding: UTF-8 -*-

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
        from sine_plot import MainWindow

    model = SineModel()
    window = MainWindow(model=model)
    window.show()

if __name__ == '__main__':
    main()
