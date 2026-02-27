import os
import sys
sys.path.insert(0, '../src')

import sys
from PySide6 import QtWidgets, QtCore
from edpac.zoo.zoo import Zoo

from edpac.visualisation.zoo_visualizer import ZooVisualizer
from edpac.visualisation.input_visualizer import InputVisualizer

def main():
    app = QtWidgets.QApplication(sys.argv)

    #################################### Zoo ######################################
    # 1. Initialize Data
    zoo = Zoo(data_dir="/home/INT/meunier.d/Tools/Packages/pyEdPac/data")
    zoo.load_everything(screen_file="screen.0", menagerie_file= "menagerie.txt")

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

        #input_viz.display_inputs(inputs)

    timer = QtCore.QTimer()
    timer.timeout.connect(update)
    timer.start(100) # 10 FPS

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
