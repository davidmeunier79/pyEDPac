import os
import sys
sys.path.insert(0, '../src')

import numpy as np

#from visualizer import BaseVisualizer,PatternVisualizer

from edpac.zoo.zoo import Zoo
#from network import Network

from edpac.ed_network.ed_synapse import EDSynapse


from edpac.ed_network.evo_network import EvoNetwork

from edpac.config.constants import *
from edpac.config.physiology_config import NeuronConfig

from PySide6 import QtWidgets, QtCore
from edpac.visualisation.network_visualizer import NetworkVisualizer


from edpac.genetic_algorithm.chromosome import Chromosome

from edpac.config.constants import *
from edpac.config.ga_config import ChromosomeConfig

def main():
    # Create objects
    chromo_config = ChromosomeConfig()

    chromosome = Chromosome(chromo_config)
    print(chromosome)

    net = EvoNetwork(chromosome, neuron_config = NeuronConfig())

    print(net)


    app = QtWidgets.QApplication(sys.argv)

    # Create visualizer (800x600 pixels, scaled up 2x for visibility)
    viz_net = NetworkVisualizer( scale=5, title = "EDPac network visualizer")
    viz_net.show()

    # initilisation
    viz_net.init_network(network=net)
    viz_net.display_network()
    viz_net.update_display()
    #
    # 0/0
    #
    # print("Before injections:" , EDSynapse.event_manager.get_nb_events())
    # ### add random stim to event_manager
    pattern_float = np.random.random(size=(VISIO_SQRT_NB_NEURONS*  VISIO_SQRT_NB_NEURONS))

    net.inject_input_float(assembly_idx=0, time=0, pattern_float=pattern_float)

    def run_simulation_step():
        """
        This replaces your old C++ while(1) loop logic.
        """
        # 1. Logic: Clear the screen
        #viz_net.clear_canvas((20, 20, 20)) # Dark gray background

        events = EDSynapse.event_manager.run_one_step()

        viz_net.display_network()

        if events is not None:
            #print(events)
            viz_net.update_visu(events)

        else:
            print("No more events in event manager, breaking")

        viz_net.update_display()

    #
    # Use a QTimer to run the simulation at ~60 FPS
    timer = QtCore.QTimer()
    timer.timeout.connect(lambda: run_simulation_step())
    timer.start(16) # 16ms = 60fps

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
