import os
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

from edpac.config.ga_config import ChromosomeConfig
from edpac.config.constants import MINIMAL_TIME, DATA_PATH



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

def evaluate_individual(indiv):

    global SIMULATION_ACTIVE
    if not SIMULATION_ACTIVE:
        return 0

    #app = QtWidgets.QApplication(sys.argv)



    zoo_viz = ZooVisualizer(width=800, height=500, scale=2)

    zoo = Zoo(data_dir=DATA_PATH)


    # Connect the "X" button of the window to our stop function
    # Note: Use the attribute 'setAttribute(QtCore.Qt.WA_DeleteOnClose)'
    # if 'destroyed' signal doesn't fire immediately.
    zoo_viz.setAttribute(Qt.WA_DeleteOnClose)
    zoo_viz.destroyed.connect(stop_everything)


    #################################### Zoo ######################################
    # 1. Initialize Data
    zoo.load_everything(screen_file="screen.0", menagerie_file= "menagerie.txt")

    ################################## Inputs #####################################
    # 2. Input/Sensor View (The new class)
    input_viz = InputVisualizer(scale=2)

    input_viz.setAttribute(Qt.WA_DeleteOnClose)
    input_viz.destroyed.connect(stop_everything)

    input_viz.setWindowTitle("Pacman Sensors")
    input_viz.show()

    ################################### Network Vizualisaer ################################

    # Create visualizer (800x600 pixels, scaled up 2x for visibility)
    viz_net = NetworkVisualizer( width=300, height=200, scale=5, title = "EDPac network visualizer")

    viz_net.setAttribute(Qt.WA_DeleteOnClose)
    viz_net.destroyed.connect(stop_everything)

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
    zoo_viz.show()

    # 3. Initial Draw
    zoo_viz.draw_zoo(zoo)

    print(zoo)

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
            loop.quit()  # This breaks the loop.exec_() below
        # Get simulated inputs (e.g., [Wall, Empty, Food, Wall, Animal])
        #mock_inputs = [1, 0, 2, 1, 3]



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
    loop.exec_()

    # 5. Now we can finally return the value to the EA
    return EDSynapse.event_manager.get_time()

def main():

    global SIMULATION_ACTIVE


    # Create objects
    chromo_config = ChromosomeConfig()

    population = Population(chromo_config)

    for i, ind in enumerate(population.individuals):
        # Check the flag BEFORE starting the next individual
        if not SIMULATION_ACTIVE:
            break

        score = evaluate_individual(ind)
        print(f"Gen {i} Fitness: {score}")

    print("Evolution finished or aborted.")


    #
    #
    #
    # # 1. Create the application once at the top level
    # app = QtWidgets.QApplication.instance()
    #
    # # Create objects
    # chromo_config = ChromosomeConfig()
    #
    # pop = Population(chromo_config)
    #
    # pop.evaluate(evaluate_individual, app)
    #
    # sys.exit(app.exec())
    #

if __name__ == "__main__":
    main()
