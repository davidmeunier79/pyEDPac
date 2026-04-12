import os
import gc

import sys
sys.path.insert(0, '../src')

from PySide6.QtCore import QEventLoop, QTimer, Qt
from PySide6 import QtWidgets

#
#
# # Force Qt to use the 'offscreen' platform (no window needed)
# os.environ["QT_QPA_PLATFORM"] = "offscreen"
#
# # Disable DBus warnings on clusters
# os.environ["QT_NO_GLIB"] = "1"

from joblib import Parallel, delayed

from edpac.zoo.zoo import Zoo, Pacman

from edpac.genetic_algorithm.population import Population
from edpac.genetic_algorithm.chromosome import Chromosome

from edpac.ed_network.evo_network import EvoNetwork
from edpac.ed_network.ed_synapse import EDSynapse

from edpac.config.constants import MINIMAL_TIME

from edpac.config.ga_config import PopulationConfigTest, SelectionConfigTest
from edpac.config.ga_config import PopulationConfig, PopulationConfigMulti, PopulationConfigMultiTest

from edpac.tracer.network_tracer import NetworkTracer

from edpac.visualisation.zoo_visualizer import ZooVisualizer
from edpac.visualisation.multi_input_visualizer import MultiInputVisualizer

from multipac.parallel.parallel_zoo import ParallelZoo

from edpac.config.config_manager import save_configs





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

def main(stats_path):

    global SIMULATION_ACTIVE
    if not SIMULATION_ACTIVE:
        return 0

    # Create objects
    #################################### Population ######################################
    zoo = ParallelZoo(pop_config = PopulationConfigMulti())
    #zoo.load_screen(screen_file="screen.empty")

    # 3. Initial Draw
    zoo.init_empty_zoo()
    zoo.deploy() # parallel zoo
    zoo.distribute_chromosomes() #parallel zoo

    ################################### Zoo Visualizer ################################
    zoo_viz = ZooVisualizer(zoo, title = "EDPac zoo")
    # Connect the "X" button of the window to our stop function
    # Note: Use the attribute 'setAttribute(QtCore.Qt.WA_DeleteOnClose)'
    # if 'destroyed' signal doesn't fire immediately.

    zoo_viz.setAttribute(Qt.WA_DeleteOnClose)
    zoo_viz.destroyed.connect(stop_everything)

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
    zoo.initialize_all_inputs()

    #
    # input_percepts = zoo.compute_zoo_interaction()
    #
    # # display percepts in multi_input_viz
    # multi_input_viz.display_all_inputs(input_percepts)
    # multi_input_viz.update_display()
    # QtWidgets.QApplication.processEvents()
    #
    # zoo.send_first_wave(input_percepts)

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
        #
        global TIME
        #
        print(f"{TIME=}")

        zoo.init_stats()
        zoo.stats["time"][-1] = TIME

        # Update both windows
        zoo_viz.draw_zoo()
        zoo_viz.update_display()
        QtWidgets.QApplication.processEvents()

        input_percepts = zoo.run_one_non_blocking_step()

        # display percepts in multi_input_viz
        multi_input_viz.display_all_inputs(input_percepts)
        multi_input_viz.update_display()
        QtWidgets.QApplication.processEvents()

        #nb_alive_indiv = zoo.test_pacman_contacts()  # Update the model()

        if zoo.stats["nb_predators"][-1]:
            zoo.stats["mean_predator_fitness"][-1] /= zoo.stats["nb_predators"][-1]

        if zoo.stats["nb_preys"][-1]:
            zoo.stats["mean_prey_fitness"][-1] /= zoo.stats["nb_preys"][-1]

        zoo.stats["generation"][-1] = zoo.population.generation

        nb_alive_indiv = len([pac for pac in zoo.population.individuals if pac])

        print(f"******************** {nb_alive_indiv=} ***********************")

        print(f"nb_preys={zoo.stats["nb_preys"][-1]} nb_predators={zoo.stats["nb_predators"][-1]} mean_prey_fitness={zoo.stats["mean_prey_fitness"][-1]} mean_predator_fitness={zoo.stats["mean_predator_fitness"][-1]} generation={zoo.stats["generation"][-1]}, nb_deads={zoo.stats["nb_deads"][-1]}, nb_added_pacgums={zoo.stats["nb_added_pacgums"][-1]}")

        if nb_alive_indiv == 0:
            print("All individuals are dead , Breaking")
            SIMULATION_ACTIVE = False


        TIME+=1


    print("In run_population")

    global TIME
    TIME = 0

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

    print("shutdown")
    zoo.shutdown()

    print("save stats")
    zoo.save_stats(stats_path)

    zoo.population.save_individuals(stats_path)

    print("save config")
    save_configs(stats_path)

    # --- CRITICAL CLEANUP STEP ---
    # 2. Disconnect signals to allow the GC to see these objects as 'dead'
    timer.timeout.disconnect(update)

    del timer
    del loop




    print("Evolution finished or aborted.")

if __name__ == "__main__":
    import time
    import argparse

    parser = argparse.ArgumentParser(description="Process a specific individual genome/path.")

    # Define the parameter
    parser.add_argument(
        "--stats_path",
        type=str,
        required=True,
        help="Path to the individual .npy or chromosome file"
    )

    # Parse and execute
    args = parser.parse_args()

    start_time = time.time()
    main(args.stats_path)
    print("--- %s seconds ---" % (time.time() - start_time))
