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

def run_simulation_step(viz_net):
    """
    This replaces your old C++ while(1) loop logic.
    """
    # 1. Logic: Clear the screen
    #viz_net.clear_canvas((20, 20, 20)) # Dark gray background


    spike_neuron_ids = EDSynapse.event_manager.run_one_step()

    if spike_neuron_ids is not None:

        print("Nb spikes: ", len(spike_neuron_ids))
        viz_net.display_spikes(spike_neuron_ids)

    else:
        print("No spike_neuron_ids , breaking")

    #viz_net.update_display()

def main():
    # Create objects
    chromo_config = ChromosomeConfig()

    chromosome = Chromosome(chromo_config)

    net = EvoNetwork(chromosome, neuron_config = NeuronConfig())

    print(net)


    app = QtWidgets.QApplication(sys.argv)

    # Create visualizer (800x600 pixels, scaled up 2x for visibility)
    viz_net = NetworkVisualizer(net, title = "EDPac network visualizer")
    viz_net.show()

    # initilisation
    #viz_net.init_network(network=net)
    viz_net.draw_assemblies()
    viz_net.update_display()
    #
    # 0/0
    #
    # print("Before injections:" , EDSynapse.event_manager.get_nb_events())
    # ### add random stim to event_manager

    net.initialize_inputs()
    #pattern_float = np.random.random(size=(VISIO_SQRT_NB_NEURONS*  VISIO_SQRT_NB_NEURONS))

    #net.inject_input_float(assembly_idx=0, time=0, pattern_float=pattern_float)

    #
    # Use a QTimer to run the simulation at ~60 FPS
    timer = QtCore.QTimer()
    timer.timeout.connect(lambda: run_simulation_step(viz_net))
    timer.start(16) # 16ms = 60fps

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
