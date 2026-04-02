import os
import sys
sys.path.insert(0, '../src')

import sys
from PySide6 import QtWidgets, QtCore
from edpac.zoo.zoo import Zoo, Pacman

from edpac.visualisation.zoo_visualizer import ZooVisualizer
from edpac.visualisation.input_visualizer import InputVisualizer
from edpac.visualisation.network_visualizer import NetworkVisualizer

from edpac.genetic_algorithm.chromosome import Chromosome

from edpac.ed_network.evo_network import EvoNetwork
from edpac.ed_network.ed_synapse import EDSynapse

from edpac.config.ga_config import ChromosomeConfig
from edpac.config.constants import MINIMAL_TIME


def main():
    app = QtWidgets.QApplication(sys.argv)

    ################################# Pacman ###########################

    # Create objects
    chromo_config = ChromosomeConfig()

    chromosome = Chromosome(chromo_config)
    print(chromosome)

    pac = Pacman(chromosome)

    #################################### Zoo ######################################
    # 1. Initialize Data
    zoo = Zoo()
    zoo.load_menagerie(menagerie_file= "menagerie.txt")

    zoo.set_pacman(pac)






    # 2. Initialize Visualiser
    # Original EDPac screens were often around 40x25 characters
    # 40 * 16 = 640px, 25 * 16 = 400px
    zoo_viz = ZooVisualizer(scale=2)
    zoo_viz.show()

    ################################### Init Zoo
    zoo.load_screen(screen_file="screen.0")
    print(zoo.animals)

    # 3. Initial Draw
    zoo_viz.init_zoo(zoo)
    zoo_viz.draw_static_grid(zoo.grid)
    zoo_viz.draw_zoo()
    zoo_viz.show()

    ################################## Inputs #####################################
    # 2. Input/Sensor View (The new class)
    input_viz = InputVisualizer(scale=2)
    input_viz.setWindowTitle("Pacman Sensors")
    input_viz.show()


    ################################### EvoNetwork ################################

    net = EvoNetwork(chromosome)
    net.initialize_inputs()

    print(net)

    ################################### Network Vizualisaer ################################

    # Create visualizer (800x600 pixels, scaled up 2x for visibility)
    viz_net = NetworkVisualizer(scale=5, title = "EDPac network visualizer")
    viz_net.set_background_color(0)
    viz_net.init_assemblies(net)
    viz_net.draw_projections(net)
    viz_net.draw_assemblies()

    viz_net.show()






    #
    #
    # net.init_output_patterns()
    #
    # current_time = EDSynapse.event_manager.get_time()
    #
    #
    # while (EDSynapse.event_manager.get_time() - current_time) < MINIMAL_TIME:
    #     events = EDSynapse.event_manager.run_one_step()
    #
    #     if events is not None:
    #         viz_net.display_network()
    #
    #         #print(events)
    #         viz_net.update_visu(events)
    #
    #     else:
    #         print("No more events in event manager, breaking")
    #
    # output_patterns = net.get_output_patterns()
    # print(output_patterns)
    #
    # zoo.pacman.integrate_motor_outputs(output_patterns)
    #
    # # 0/0
    #











    # 3. Simulation Loop (simplified)
    def update():

        zoo.live_one_step()  # Update the model()

        # Update both windows
        zoo_viz.draw_zoo()

        # 1. Get sensory data from the world
        sensory_data = zoo.pacman.integrate_visio_outputs()
        #print(sensory_data)

        # 2. Update the diagnostic display (the 5 squares)
        input_viz.display_inputs(sensory_data)

        # 3 integrate to EDNetwork
        spike_neuron_ids = net.integrate_inputs(sensory_data)

        viz_net.display_spikes(spike_neuron_ids)
        viz_net.update_display()




        current_time = EDSynapse.event_manager.get_time()

        net.init_output_patterns()

        while (EDSynapse.event_manager.get_time() - current_time) < MINIMAL_TIME:
            spike_neuron_ids = EDSynapse.event_manager.run_one_step()

            if spike_neuron_ids is not None:

                viz_net.display_spikes(spike_neuron_ids)
                viz_net.update_display()
                QtWidgets.QApplication.processEvents()


            else:
                print("No more events in event manager, breaking")
                break

            viz_net.update_display()

        output_patterns = net.get_output_patterns()
        print(output_patterns)


        zoo.pacman.integrate_motor_outputs(output_patterns)


        # Get simulated inputs (e.g., [Wall, Empty, Food, Wall, Animal])
        #mock_inputs = [1, 0, 2, 1, 3]



    timer = QtCore.QTimer()
    timer.timeout.connect(update)
    timer.start(100) # 10 FPS

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
