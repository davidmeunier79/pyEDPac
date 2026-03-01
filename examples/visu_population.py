import os
import sys
sys.path.insert(0, '../src')

import sys
from PySide6 import QtWidgets, QtCore
from edpac.zoo.zoo import Zoo, Pacman

from edpac.visualisation.zoo_visualizer import ZooVisualizer
from edpac.visualisation.input_visualizer import InputVisualizer
from edpac.visualisation.network_visualizer import NetworkVisualizer

from edpac.genetic_algorithm.population import Population
from edpac.genetic_algorithm.chromosome import Chromosome

from edpac.ed_network.evo_network import EvoNetwork
from edpac.ed_network.ed_synapse import EDSynapse

from edpac.config.ga_config import ChromosomeConfig
from edpac.config.constants import MINIMAL_TIME





def evaluate_individual(indiv):

    app = QtWidgets.QApplication(sys.argv)



    #################################### Zoo ######################################
    # 1. Initialize Data
    zoo = Zoo(data_dir="/home/INT/meunier.d/Tools/Packages/pyEdPac/data")
    zoo.load_everything(screen_file="screen.0", menagerie_file= "menagerie.txt")

    ################################## Inputs #####################################
    # 2. Input/Sensor View (The new class)
    input_viz = InputVisualizer(scale=2)
    input_viz.setWindowTitle("Pacman Sensors")
    input_viz.show()

    ################################### Network Vizualisaer ################################

    # Create visualizer (800x600 pixels, scaled up 2x for visibility)
    viz_net = NetworkVisualizer( width=300, height=200, scale=5, title = "EDPac network visualizer")
    viz_net.show()


    ################################# Pacman ###########################


    print(indiv)

    pac = Pacman(indiv)

    zoo.set_pacman(pac)

    ################################### EvoNetwork ################################

    net = EvoNetwork(indiv.get_chromosome())
    net.initialize_inputs()

    print(net)

    # initilisation
    viz_net.init_network(network=net)
    viz_net.display_network()
    viz_net.update_display()

    #################################### Zoo Visualiser ###################################
    # 2. Initialize Visualiser
    # Original EDPac screens were often around 40x25 characters
    # 40 * 16 = 640px, 25 * 16 = 400px
    zoo_viz = ZooVisualizer(width=800, height=500, scale=2)
    zoo_viz.show()

    # 3. Initial Draw
    zoo_viz.draw_zoo(zoo)

    print(zoo)

    # 3. Simulation Loop (simplified)
    def update():

        zoo.live_one_step()  # Update the model()

        # Update both windows
        zoo_viz.draw_zoo(zoo)

        # 1. Get sensory data from the world
        sensory_data = zoo.pacman.integrate_visio_outputs()
        #print(sensory_data)

        # 2. Update the diagnostic display (the 5 squares)
        input_viz.display_inputs(sensory_data)

        # 3 integrate to EDNetwork
        net.integrate_inputs(sensory_data)

        viz_net.update_display()

        current_time = EDSynapse.event_manager.get_time()

        net.init_output_patterns()

        while (EDSynapse.event_manager.get_time() - current_time) < MINIMAL_TIME:
            events = EDSynapse.event_manager.run_one_step()

            if events is not None:
                viz_net.display_network()

                #print(events)
                viz_net.update_visu(events)

            else:
                print("No more events in event manager, breaking")
                break

            viz_net.update_display()

        output_patterns = net.get_output_patterns()
        print(output_patterns)


        zoo.pacman.integrate_motor_outputs(output_patterns)

        zoo.pacman.life_points = zoo.pacman.life_points -1

        if zoo.pacman.life_points < 0:
            print("Individual is dead, breaking")
            return EDSynapse.event_manager.get_time()
        # Get simulated inputs (e.g., [Wall, Empty, Food, Wall, Animal])
        #mock_inputs = [1, 0, 2, 1, 3]



    timer = QtCore.QTimer()
    timer.timeout.connect(update)
    timer.start(100) # 10 FPS


    sys.exit(app.exec())


def main():


    # Create objects
    chromo_config = ChromosomeConfig()

    pop = Population(chromo_config)

    pop.evaluate(evaluate_individual)

if __name__ == "__main__":
    main()
