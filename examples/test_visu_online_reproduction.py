import os
import gc

import sys
sys.path.insert(0, '../src')

from PySide6.QtCore import QEventLoop, QTimer, Qt
from PySide6 import QtWidgets

from joblib import Parallel, delayed

from edpac.zoo.zoo import Zoo, Pacman
from edpac.zoo.chars import index_to_char, char_to_index

from edpac.genetic_algorithm.population import Population
from edpac.genetic_algorithm.chromosome import Chromosome

from edpac.ed_network.evo_network import EvoNetwork
from edpac.ed_network.ed_synapse import EDSynapse

from edpac.config.constants import MINIMAL_TIME

from edpac.config.ga_config import PopulationConfigMultiTest, SelectionConfigTest

from edpac.tracer.network_tracer import NetworkTracer

from edpac.visualisation.zoo_visualizer import ZooVisualizer

from multipac.parallel.parallel_zoo import ParallelZoo

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


def main():



    # Create objects
    #################################### Zoo ######################################
    # 1. Initialize Data
    pop_config = PopulationConfigMultiTest()

    pop_config.POPULATION_SIZE = 10

    pop_config.INIT_POPULATION_SIZE = 3

    zoo = ParallelZoo(pop_config = pop_config)

    zoo.load_menagerie(menagerie_file= "menagerie.txt")

    zoo.load_screen(screen_file="screen.empty")

    ################################### Zoo Visualizer ################################
    zoo_viz = ZooVisualizer(zoo, title = "EDPac zoo")
    # Connect the "X" button of the window to our stop function
    # Note: Use the attribute 'setAttribute(QtCore.Qt.WA_DeleteOnClose)'
    # if 'destroyed' signal doesn't fire immediately.

    zoo_viz.setAttribute(Qt.WA_DeleteOnClose)
    zoo_viz.destroyed.connect(stop_everything)

    #zoo_viz.init_zoo(zoo)
    zoo_viz.draw_static_grid()
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

        global MAX_TIME

        print(f"{MAX_TIME=}")



        #zoo.init_empty_zoo()
        pac = zoo.population.individuals[0]
        pac.set_animal_nature("1")
        pac.set_position(10, 11)
        zoo._set_in_grid(10, 11, index_to_char(0))


        pac = zoo.population.individuals[1]
        pac.set_animal_nature("-1")
        pac.set_position(5, 18)
        zoo._set_in_grid(5, 18, index_to_char(1))


        pac = zoo.population.individuals[2]
        pac.set_animal_nature("1")
        pac.set_position(10, 12)
        zoo._set_in_grid(10, 12, index_to_char(2))

        # Update both windows
        zoo_viz.draw_zoo()
        zoo_viz.update_display()
        QtWidgets.QApplication.processEvents()

        time.sleep(2.5)

        zoo.deploy()

        zoo.test_pacman_contacts()

        # Update both windows
        zoo_viz.draw_zoo()
        zoo_viz.update_display()
        QtWidgets.QApplication.processEvents()

        MAX_TIME -= 1

    print("In run_population")

    global MAX_TIME
    MAX_TIME = 100

    # timer = QtCore.QTimer()
    # timer.timeout.connect(update)
    # timer.start(100) # 10 FPS
    #
    #
    # sys.exit(app.exec())

    # 3. Set up the timer
    timer = QTimer()
    timer.timeout.connect(update)
    timer.start(10) # Run fast for evaluation

    # 4. BLOCK here until loop.quit() is called
    loop.exec()

    # --- CRITICAL CLEANUP STEP ---
    # 2. Disconnect signals to allow the GC to see these objects as 'dead'
    timer.timeout.disconnect(update)

    del timer
    del loop








if __name__ == "__main__":
    import time
    start_time = time.time()
    main()
    print("--- %s seconds ---" % (time.time() - start_time))
