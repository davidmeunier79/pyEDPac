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
from edpac.visualisation.network_visualizer import NetworkVisualizer

from edpac.genetic_algorithm.population import Population
from edpac.genetic_algorithm.chromosome import Chromosome

from edpac.ed_network.evo_network import EvoNetwork
from edpac.ed_network.ed_synapse import EDSynapse

from edpac.config.constants import MINIMAL_TIME, DATA_PATH

from edpac.config.ga_config import PopulationConfig

import time


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


    #################################### Zoo ######################################
    # 1. Initialize Data
    zoo = Zoo(data_dir=DATA_PATH)
    zoo.load_menagerie(menagerie_file= "menagerie.txt")

    ################################# Pacman ###########################

    ################################### Zoo Visualizer ################################
    zoo_viz = ZooVisualizer(title = "EDPac zoo")
    # Connect the "X" button of the window to our stop function
    # Note: Use the attribute 'setAttribute(QtCore.Qt.WA_DeleteOnClose)'
    # if 'destroyed' signal doesn't fire immediately.
    zoo_viz.setAttribute(Qt.WA_DeleteOnClose)
    zoo_viz.destroyed.connect(stop_everything)

    #
    # ################################### Network Visualizer ################################
    # # Create visualizer (800x600 pixels, scaled up 2x for visibility)
    # net_viz = NetworkVisualizer(title = "EDPac network", scale = 2)
    # net_viz.setAttribute(Qt.WA_DeleteOnClose)
    # net_viz.destroyed.connect(stop_everything)
#
#     ################################### EvoNetwork ################################
#
#     net = EvoNetwork(indiv.get_chromosome())
#     net.initialize_inputs()
#
#     print(net)
#
#     # initilisation
#
#     net_viz.init_network(net)
#     net_viz.setup_topology()
#     net_viz.show()
#
    ################################## Inputs Visualizer #####################################
    # 2. Input/Sensor View (The new class)
    input_viz = InputVisualizer(title = "EDPac inputs", scale = 2)
    input_viz.setAttribute(Qt.WA_DeleteOnClose)
    input_viz.destroyed.connect(stop_everything)

    # input_viz
    input_viz.draw_background()
    input_viz.show()

    ################################## Pacman ################################################
    pac = Pacman()
    zoo.set_pacman(pac)

    ################################### Init Zoo
    zoo.load_screen(screen_file="screen.0")
    print(zoo.animals)

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


        zoo.test_pacman_contacts()

        # 1. Get sensory data from the world
        sensory_data = zoo.pacman.integrate_visio_outputs()
        #print(sensory_data)

        # 2. Update the diagnostic display (the 5 squares)
        input_viz.display_inputs(sensory_data)

        time.sleep(2.5)

        # turn 90deg to the right
        pac.dir_head = pac._get_turn(pac.dir_head , 1)

        #
        # # 3 integrate to EDNetwork
        # net.integrate_inputs(sensory_data)
        #
        # current_time = EDSynapse.event_manager.get_time()
        #
        # net.init_output_patterns()
        #
        # while (EDSynapse.event_manager.get_time() - current_time) < MINIMAL_TIME:
        #
        #     #net_viz.display_empty_network()
        #
        #     spike_neuron_ids = EDSynapse.event_manager.run_one_step()
        #
        #     if spike_neuron_ids is not None:
        #
        #         #print("Nb spikes: ", len(spike_neuron_ids))
        #         net_viz.display_spikes(spike_neuron_ids)
        #
        #     else:
        #         print("No more events in event manager, breaking")
        #         break
        #
        # output_patterns = net.get_output_patterns()
        # print(output_patterns)

        #
        # zoo.pacman.integrate_motor_outputs(output_patterns)
        #
        # zoo.pacman.life_points = zoo.pacman.life_points -1
        #
        # if zoo.pacman.life_points < 0:
        #     print("Individual is dead, breaking")
        #     loop.quit()  # This breaks the loop.exec_() below
        # # Get simulated inputs (e.g., [Wall, Empty, Food, Wall, Animal])
        # #mock_inputs = [1, 0, 2, 1, 3]



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
