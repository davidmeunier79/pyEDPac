import os
import gc

import sys
sys.path.insert(0, '../src')

import sys
from PySide6.QtCore import QEventLoop, QTimer, Qt
from PySide6 import QtWidgets

from edpac.zoo.zoo import Zoo, Pacman

from edpac.visualisation.zoo_visualizer import ZooVisualizer
from edpac.visualisation.input_visualizer import InputVisualizer

from edpac.visualisation.multi_input_visualizer import MultiInputVisualizer

from edpac.visualisation.network_visualizer import NetworkVisualizer

from edpac.genetic_algorithm.population import Population
from edpac.genetic_algorithm.chromosome import Chromosome

from edpac.ed_network.evo_network import EvoNetwork
from edpac.ed_network.ed_synapse import EDSynapse

from edpac.config.constants import MINIMAL_TIME

from edpac.config.ga_config import PopulationConfig, PopulationConfigMultiTest

import time


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

    global SIMULATION_ACTIVE
    if not SIMULATION_ACTIVE:
        return 0

    # Create objects
    #################################### Population ######################################
    zoo = ParallelZoo(config = PopulationConfigMultiTest())
    #zoo.load_screen(screen_file="screen.empty")

    # 3. Initial Draw
    zoo.init_empty_zoo()

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


    ####################################### MultiInputVisualizer ########################
    multi_input_viz = MultiInputVisualizer(zoo.population, title = "EDPac inputs")
    # Connect the "X" button of the window to our stop function
    # Note: Use the attribute 'setAttribute(QtCore.Qt.WA_DeleteOnClose)'
    # if 'destroyed' signal doesn't fire immediately.

    multi_input_viz.setAttribute(Qt.WA_DeleteOnClose)
    multi_input_viz.destroyed.connect(stop_everything)

    #zoo_viz.init_zoo(zoo)
    #zoo_viz.draw_static_grid()
    #zoo_viz.draw_zoo()

    multi_input_viz.display_all_backgrounds()
    multi_input_viz.show()

    #multi_input_viz.update_display()
    QtWidgets.QApplication.processEvents()


    print("Running population")
    zoo.population.initialize_all_inputs()


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

        print(MAX_TIME)

        print("Init: dirhead = ", zoo.population.individuals[0].dir_head.to_string())
        print("Init: dirbody = ", zoo.population.individuals[0].dir_body.to_string())

        # Update both windows
        zoo_viz.draw_zoo()
        zoo_viz.update_display()
        #QtWidgets.QApplication.processEvents()

        input_percepts = zoo.compute_zoo_interaction()
        #print(f"{input_percepts=}")

        # display percepts in multi_input_viz
        multi_input_viz.display_all_inputs(input_percepts)
        multi_input_viz.update_display()
        QtWidgets.QApplication.processEvents()

        time.sleep(2.5)

        # turn 90deg to the right
        zoo.turn_all_heads(1)

        print("Turn head: dirhead = ", zoo.population.individuals[0].dir_head.to_string())
        print("Turn head: dirbody = ", zoo.population.individuals[0].dir_body.to_string())


        # Update both windows
        zoo_viz.draw_zoo()
        zoo_viz.update_display()
        #QtWidgets.QApplication.processEvents()

        input_percepts = zoo.compute_zoo_interaction()
        #print(f"{input_percepts=}")

        # display percepts in multi_input_viz
        multi_input_viz.display_all_inputs(input_percepts)
        multi_input_viz.update_display()
        QtWidgets.QApplication.processEvents()

        time.sleep(2.5)

        # turn 90deg to the right
        zoo.turn_all_body(1)

        print("Turn body: dirhead = ", zoo.population.individuals[0].dir_head.to_string())
        print("Turn body: dirbody = ", zoo.population.individuals[0].dir_body.to_string())

        # Update both windows
        zoo_viz.draw_zoo()
        zoo_viz.update_display()
        #QtWidgets.QApplication.processEvents()

        input_percepts = zoo.compute_zoo_interaction()
        #print(f"{input_percepts=}")

        # display percepts in multi_input_viz
        multi_input_viz.display_all_inputs(input_percepts)
        multi_input_viz.update_display()
        QtWidgets.QApplication.processEvents()

        time.sleep(2.5)

        # move forward with dir body
        zoo.all_move_forward()

        print("Move forward: dirhead = ", zoo.population.individuals[0].dir_head.to_string())
        print("Move forward: dirbody = ", zoo.population.individuals[0].dir_body.to_string())

        # Update both windows
        zoo_viz.draw_zoo()
        zoo_viz.update_display()
        #QtWidgets.QApplication.processEvents()

        #time.sleep(2.5)

        input_percepts = zoo.compute_zoo_interaction()
        #print(f"{input_percepts=}")

        # display percepts in multi_input_viz
        multi_input_viz.display_all_inputs(input_percepts)
        multi_input_viz.update_display()
        QtWidgets.QApplication.processEvents()

        time.sleep(2.5)

        ## break conditions
        if all([indiv == 0 for indiv in zoo.population.individuals]) == True:
            print("All individuals are dead , Breaking")

            SIMULATION_ACTIVE = False

        MAX_TIME -= 1

        if MAX_TIME < 0 or SIMULATION_ACTIVE==False:
            print(f"In shutting_down at {MAX_TIME=}")
            loop.quit()

            zoo.population.shutdown()


    print("In run_population")

    global MAX_TIME
    MAX_TIME = 10


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
