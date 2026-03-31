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

from edpac.config.constants import MINIMAL_TIME

from edpac.tracer.network_tracer import NetworkTracer

from edpac.config.ga_config import PopulationConfigTest, SelectionConfigTest


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

def evaluate_individual(indiv, zoo, zoo_viz, net_viz, input_viz, path_indiv):

    global empty_events
    empty_events= False

    global SIMULATION_ACTIVE
    if not SIMULATION_ACTIVE:
        return 0

    #app = QtWidgets.QApplication(sys.argv)


    pac = Pacman(indiv)
    zoo.set_pacman(pac)
    zoo.load_screen(screen_file="screen.0")

    # 3. Initial Draw
    zoo_viz.init_zoo(zoo)
    zoo_viz.draw_static_grid(zoo.grid)
    zoo_viz.draw_zoo()
    zoo_viz.show()

    ################################### EvoNetwork ################################

    net = EvoNetwork(indiv)
    net.initialize_inputs()

    print(net)

    # initilisation visu
    net_viz.set_background_color(0)
    net_viz.init_assemblies(net)
    net_viz.draw_projections(net)
    net_viz.draw_assemblies()
    net_viz.show()

    net_viz.refresh_from_background()
    net_viz.update_display()
    QtWidgets.QApplication.processEvents()

    # NetworkTracer
    spike_neuron_ids = net.initialize_inputs()

    network_tracer = NetworkTracer(net)
    network_tracer.record(0, spike_neuron_ids)

    #################################### Inputs ####################################
    # input_viz
    input_viz.draw_background()
    input_viz.show()


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

        global empty_events

        zoo.live_one_step()  # Update the model()

        # Update both windows
        zoo_viz.draw_zoo()


        zoo.test_pacman_contacts()

        # 1. Get sensory data from the world
        sensory_data = zoo.pacman.integrate_visio_outputs()
        #print(sensory_data)

        # 2. Update the diagnostic display (the 5 squares)
        input_viz.display_inputs(sensory_data)

        # 3 integrate to EDNetwork
        spike_neuron_ids = net.integrate_inputs(sensory_data)

        net_viz.display_spikes(spike_neuron_ids)
        net_viz.update_display()
        QtWidgets.QApplication.processEvents()

        current_time = EDSynapse.event_manager.get_time()

        net.init_output_patterns()

        while (EDSynapse.event_manager.get_time() - current_time) < MINIMAL_TIME:

            time_before = EDSynapse.event_manager.get_time()
            spike_neuron_ids = EDSynapse.event_manager.run_one_step()

            if spike_neuron_ids is not None:

                net_viz.display_spikes(spike_neuron_ids)
                net_viz.update_display()
                QtWidgets.QApplication.processEvents()


                network_tracer.record(time_before, spike_neuron_ids)

            else:
                print("No spikes in event manager")
                net_viz.refresh_from_background()
                net_viz.update_display()
                QtWidgets.QApplication.processEvents()


            if EDSynapse.event_manager.get_nb_events() == 0:
                print("No more events in event manager, breaking")
                zoo.pacman.life_points = -100
                empty_events = True
                break

        output_patterns = net.get_output_patterns()

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
    loop.exec()

    # --- CRITICAL CLEANUP STEP ---
    # 2. Disconnect signals to allow the GC to see these objects as 'dead'
    timer.timeout.disconnect(update)

    del timer
    del loop

    print("After Loop")


    network_tracer.plot(target_dir = path_indiv)

    # 5. Now we can finally return the value to the EA
    score = EDSynapse.event_manager.get_time()
    indiv.set_fitness(score)
    indiv.save_genes(path_indiv)

    # saving chromosome
    indiv.save_genes(path_indiv)
    indiv.save_stats(path_indiv)
    pac.save_stats(path_indiv)

    # saving evo_network
    net.stats["empty_events"] = empty_events

    net.save_stats(path_indiv)

    network_tracer.plot(target_dir = path_indiv)

    # 3. Explicitly delete heavy local references
    del net
    del pac

    EDSynapse.event_manager.reset()

    del EDSynapse.event_manager

    print(indiv)

def main():

    global SIMULATION_ACTIVE
    SIMULATION_ACTIVE = True


    #################################### Zoo ######################################
    # 1. Initialize Data
    zoo = Zoo()
    zoo.load_menagerie(menagerie_file= "menagerie.txt")

    ################################# Pacman ###########################

    ################################### Zoo Visualizer ################################
    zoo_viz = ZooVisualizer(title = "EDPac zoo")
    # Connect the "X" button of the window to our stop function
    # Note: Use the attribute 'setAttribute(QtCore.Qt.WA_DeleteOnClose)'
    # if 'destroyed' signal doesn't fire immediately.
    zoo_viz.setAttribute(Qt.WA_DeleteOnClose)
    zoo_viz.destroyed.connect(stop_everything)


    ################################### Network Visualizer ################################
    # Create visualizer (800x600 pixels, scaled up 2x for visibility)
    net_viz = NetworkVisualizer(title = "EDPac network", scale = 2)
    net_viz.setAttribute(Qt.WA_DeleteOnClose)
    net_viz.destroyed.connect(stop_everything)

    ################################## Inputs Visualizer #####################################
    # 2. Input/Sensor View (The new class)
    input_viz = InputVisualizer(title = "EDPac inputs", scale = 2)
    input_viz.setAttribute(Qt.WA_DeleteOnClose)
    input_viz.destroyed.connect(stop_everything)

    # Create objects
    #################################### Population ######################################

    #population = Population()

    population = Population(selection_config = SelectionConfigTest(), config = PopulationConfigTest())


    for gen in range(population.config.NB_GENERATIONS):

        print(f"Starting Generation {gen}")

        for i, ind in enumerate(population.individuals):
            # Check the flag BEFORE starting the next individual
            if not SIMULATION_ACTIVE:
                print("Simualtion is over, breaking")
                break

            path_indiv = os.path.abspath(f"Gen_{gen}/Ind_{i}/")

            try:
                os.makedirs(path_indiv)

            except OSError as e:
                print(f"Error {e}")


            evaluate_individual(ind, zoo, zoo_viz, net_viz, input_viz, path_indiv)

            print("SIMULATION_ACTIVE = ", SIMULATION_ACTIVE)
            # 5. Force Python to reclaim memory now rather than 'whenever'
            # This is especially helpful when dealing with large neural networks
            gc.collect()

        population.evolve_generation()

    print("Evolution finished or aborted.")
    print(population.fitness_history)


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
    import time
    start_time = time.time()
    main()
    print("--- %s seconds ---" % (time.time() - start_time))
