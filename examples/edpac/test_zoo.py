import os
import gc

import sys
sys.path.insert(0, '../src')

import sys
from PySide6.QtCore import QEventLoop, QTimer, Qt
from PySide6 import QtWidgets

from edpac.zoo.zoo import Zoo, Pacman

from edpac.visualisation.zoo_visualizer import ZooVisualizer
#from edpac.visualisation.input_visualizer import InputVisualizer
#from edpac.visualisation.network_visualizer import NetworkVisualizer

#from edpac.genetic_algorithm.population import Population
#from edpac.genetic_algorithm.chromosome import Chromosome

#from edpac.ed_network.evo_network import EvoNetwork
#from edpac.ed_network.ed_synapse import EDSynapse

from edpac.config.constants import MINIMAL_TIME

from edpac.config.ga_config import PopulationConfig


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


    zoo = Zoo()
    #################################### Zoo ######################################
    # 1. Initialize Data
    zoo.load_menagerie(menagerie_file= "menagerie.txt")

    ################################# Pacman ###########################

    pac = Pacman()
    zoo.set_pacman(pac)


    zoo.load_screen(screen_file="screen.0")

    ################################### Zoo Visualizer ################################
    zoo_viz = ZooVisualizer(title = "EDPac zoo")

    # Connect the "X" button of the window to our stop function
    # Note: Use the attribute 'setAttribute(QtCore.Qt.WA_DeleteOnClose)'
    # if 'destroyed' signal doesn't fire immediately.
    zoo_viz.setAttribute(Qt.WA_DeleteOnClose)
    zoo_viz.destroyed.connect(stop_everything)

    # 3. Initial Draw
    zoo_viz.init_zoo(zoo)
    zoo_viz.draw_static_grid(zoo.grid)
    zoo_viz.draw_zoo()
    zoo_viz.show()



    # 2. Create a local event loop
    loop = QEventLoop()

    # 3. Simulation Loop (simplified)
    def update():

        global SIMULATION_ACTIVE

        # If the window was closed, stop this individual's evaluation
        if not SIMULATION_ACTIVE:
            timer.stop()
            loop.quit()
            return

        zoo.live_one_step()  # Update the model()

        # Update both windows
        zoo_viz.draw_zoo()

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
