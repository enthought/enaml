""" A Lotka-Volterra model. 
"""

import numpy as np

from traits.api import Array, HasTraits, Float, on_trait_change

import enaml


class LotkaVolterra(HasTraits):

    dt = Float(1./128)
    total_time = Float(20.0)

    prey0 = Float(5.0)
    predator0 = Float(2.0)
    prey_growth = Float(1.0)
    predation_rate = Float(0.2)
    predator_growth = Float(0.04)
    predator_death = Float(0.5)

    t = Array()
    prey = Array()
    predator = Array()

    @on_trait_change('dt,total_time,prey0,predator0,prey_growth,predation_rate,predator_growth,predator_death')
    def integrate(self):
        """ Use a modifed Euler's method to integrate the 
        """
        nsteps = int(round(self.total_time / self.dt))
        t = self.dt * np.arange(nsteps)
        x = self.prey0
        y = self.predator0
        prey = np.empty(nsteps)
        prey[0] = x
        predator = np.empty(nsteps)
        predator[0] = y
        for i in xrange(1, nsteps):
            x2 = x + self.dt * (self.prey_growth*x - self.predation_rate*x*y)
            y2 = y + self.dt * (-self.predator_death*y + self.predator_growth*x2*y)
            prey[i] = x2
            predator[i] = y2
            x = x2
            y = y2
        self.trait_set(
            t=t,
            prey=prey,
            predator=predator,
        )


def main():
    from simple_plot import SimplePlot
    SimplePlot.activate()

    with enaml.imports():
        from lotka_volterra_ui import MainWindow

    model = LotkaVolterra()
    model.integrate()
    window = MainWindow(model=model)
    window.show()

if __name__ == '__main__':
    main()

