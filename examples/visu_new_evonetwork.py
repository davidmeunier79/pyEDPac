import os
import sys
sys.path.insert(0, '../src')

import numpy as np

import time

#from visualizer import BaseVisualizer,PatternVisualizer

from edpac.zoo.zoo import Zoo
#from network import Network

from edpac.ed_network.ed_synapse import EDSynapse


from edpac.ed_network.evo_network import EvoNetwork

from edpac.config.constants import *
from edpac.config.physiology_config import NeuronConfig


from PySide6.QtCore import QEventLoop, QTimer, Qt
from PySide6 import QtWidgets, QtCore

from edpac.visualisation.network_visualizer import NetworkVisualizer

from edpac.visualisation.input_visualizer import InputVisualizer

from edpac.genetic_algorithm.chromosome import Chromosome

from edpac.config.constants import *
from edpac.config.ga_config import ChromosomeConfig

# 1. Global flag to track if we should keep evolving
SIMULATION_ACTIVE = True

# 1. Create the application once at the top level
app = QtWidgets.QApplication.instance()
if not app:
    app = QtWidgets.QApplication(sys.argv)

def stop_everything():
    global SIMULATION_ACTIVE
    SIMULATION_ACTIVE = False
    print("Window closed. Terminating simulation...")
    # This ensures any active QEventLoop also exits
    app.quit()


def main():

    global SIMULATION_ACTIVE
    if not SIMULATION_ACTIVE:
        return 0



    ################################### Network Visualizer ################################
    # Create visualizer (800x600 pixels, scaled up 2x for visibility)
    net_viz = NetworkVisualizer(title = "EDPac network", scale = 2)
    net_viz.setAttribute(Qt.WA_DeleteOnClose)
    net_viz.destroyed.connect(stop_everything)

    ################################## Inputs Visualizer #####################################
    # 2. Input/Sensor View (The new class)
    input_viz = InputVisualizer(title = "EDPac inputs", scale = 2)
    input_viz.setAttribute(Qt.WA_DeleteOnClose)
    input_viz.destroyed.connect(stop_everything)





    # Create objects
    chromo_config = ChromosomeConfig()

    chromosome = Chromosome(chromo_config)


    ################################### EvoNetwork ################################

    net = EvoNetwork(chromosome)

    print(net)


    # initilisation

    net_viz.init_assemblies(net)
    net_viz.draw_projections(net)
    net_viz.draw_assemblies()
    net_viz.show()

    # input_viz
    input_viz.draw_background()
    input_viz.show()





    #
    # 0/0
    #
    # print("Before injections:" , EDSynapse.event_manager.get_nb_events())
    # ### add random stim to event_manager

    spike_neuron_ids = net.initialize_inputs()

    net_viz.display_spikes(spike_neuron_ids)


    #pattern_float = np.random.random(size=(VISIO_SQRT_NB_NEURONS*  VISIO_SQRT_NB_NEURONS))

    #net.inject_input_float(assembly_idx=0, time=0, pattern_float=pattern_float)

    # 2. Create a local event loop
    loop = QEventLoop()

    def update():
        """
        This replaces your old C++ while(1) loop logic.
        """
        #
        # # 1. Get sensory data from the world
        # sensory_data = zoo.pacman.integrate_visio_outputs()
        # #print(sensory_data)

        # 2. Update the diagnostic display (the 5 squares)
        #input_viz.display_inputs(sensory_data)

        # 3 integrate to EDNetwork
        #net.integrate_inputs(sensory_data)

        global SIMULATION_ACTIVE

        # If the window was closed, stop this individual's evaluation
        if not SIMULATION_ACTIVE:
            timer.stop()
            loop.quit()
            return

        current_time = EDSynapse.event_manager.get_time()

        net.init_output_patterns()

        while (EDSynapse.event_manager.get_time() - current_time) < MINIMAL_TIME:

            spike_neuron_ids = EDSynapse.event_manager.run_one_step()

            if spike_neuron_ids is not None:

                #print(spike_neuron_ids)
                #print("Nb spikes: ", len(spike_neuron_ids))



                net_viz.display_spikes(spike_neuron_ids)
                net_viz.update_display()
                QtWidgets.QApplication.processEvents()


            else:
                print("No more events in event manager, breaking")

                net_viz.refresh_from_background()()

                net_viz.update_display()
                QtWidgets.QApplication.processEvents()


                break


        output_patterns = net.get_output_patterns()


    # 3. Set up the timer
    timer = QTimer()
    timer.timeout.connect(update)
    timer.start(10) # Run fast for evaluation

    # 4. BLOCK here until loop.quit() is called
    loop.exec()

    # --- CRITICAL CLEANUP STEP ---
    # 2. Disconnect signals to allow the GC to see these objects as 'dead'
    timer.timeout.disconnect(update)


if __name__ == "__main__":
    main()
