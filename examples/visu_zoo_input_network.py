import os
import sys
sys.path.insert(0, '../src')

import sys
from PySide6 import QtWidgets, QtCore
from edpac.zoo.zoo import Zoo, Pacman

from edpac.visualisation.zoo_visualizer import ZooVisualizer
from edpac.visualisation.input_visualizer import InputVisualizer

from edpac.genetic_algorithm.chromosome import Chromosome

from edpac.ed_network.evo_network import EvoNetwork

from edpac.config.ga_config import ChromosomeConfig

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
    zoo = Zoo(pac, data_dir="/home/INT/meunier.d/Tools/Packages/pyEdPac/data")
    zoo.load_everything(screen_file="screen.0", menagerie_file= "menagerie.txt")

    print(zoo.shapes)

    # 2. Initialize Visualiser
    # Original EDPac screens were often around 40x25 characters
    # 40 * 16 = 640px, 25 * 16 = 400px
    zoo_viz = ZooVisualizer(width=800, height=500, scale=2)
    zoo_viz.show()

    # 3. Initial Draw
    zoo_viz.draw_zoo(zoo)

    ################################## Inputs #####################################
    # 2. Input/Sensor View (The new class)
    input_viz = InputVisualizer(scale=2)
    input_viz.setWindowTitle("Pacman Sensors")
    input_viz.show()


    ################################### EvoNetwork ################################

    net = EvoNetwork(chromosome)
    net.initialize_inputs()

    print(net)


    # 3. Simulation Loop (simplified)
    def update():

        # Get simulated inputs (e.g., [Wall, Empty, Food, Wall, Animal])
        #mock_inputs = [1, 0, 2, 1, 3]

        zoo.live_one_step()  # Update the model()

        # Update both windows
        zoo_viz.draw_zoo(zoo)

        # 1. Get sensory data from the world
        sensory_data = zoo.pacman.integrate_visio_outputs()
        print(sensory_data)

        # 2. Update the diagnostic display (the 5 squares)
        input_viz.display_inputs(sensory_data)

        # 3 integrate to EDNetwork
        net.integrate_inputs(sensory_data)
        #input_viz.display_inputs(inputs)

    timer = QtCore.QTimer()
    timer.timeout.connect(update)
    timer.start(100) # 10 FPS

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
