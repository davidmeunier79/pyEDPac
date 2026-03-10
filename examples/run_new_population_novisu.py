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

from edpac.config.ga_config import PopulationConfig

def evaluate_individual(indiv, zoo, zoo_viz, net_viz, input_viz):

    pac = Pacman(indiv)
    zoo.set_pacman(pac)
    zoo.load_screen(screen_file="screen.0")

    ################################### EvoNetwork ################################

    net = EvoNetwork(indiv.get_chromosome())
    net.initialize_inputs()

    print(net)

    while zoo.pacman.life_points > 0 :

        zoo.live_one_step()  # Update the model()

        # Update both windows
        #zoo_viz.draw_zoo()


        zoo.test_pacman_contacts()

        # 1. Get sensory data from the world
        sensory_data = zoo.pacman.integrate_visio_outputs()
        #print(sensory_data)

        # 2. Update the diagnostic display (the 5 squares)
        #input_viz.display_inputs(sensory_data)

        # 3 integrate to EDNetwork
        net.integrate_inputs(sensory_data)

        current_time = EDSynapse.event_manager.get_time()

        net.init_output_patterns()

        while (EDSynapse.event_manager.get_time() - current_time) < MINIMAL_TIME:

            spike_neuron_ids = EDSynapse.event_manager.run_one_step()

            if EDSynapse.event_manager.get_nb_events() == 0:
                print("No more events in event manager, breaking")
                zoo.pacman.life_points = -100
                break

        output_patterns = net.get_output_patterns()
        print(output_patterns)


        zoo.pacman.integrate_motor_outputs(output_patterns)

        zoo.pacman.life_points = zoo.pacman.life_points -1

    # 3. Explicitly delete heavy local references
    del net
    del pac

    print("After Loop")

    # 5. Now we can finally return the value to the EA
    score = EDSynapse.event_manager.get_time()

    indiv.set_fitness(score)

    EDSynapse.event_manager.reset()

    del EDSynapse.event_manager

    print(indiv)

def main():

    #################################### Zoo ######################################
    # 1. Initialize Data
    zoo = Zoo()
    zoo.load_menagerie(menagerie_file= "menagerie.txt")

    # Create objects
    #################################### Population ######################################

    population = Population()
    pop_config = PopulationConfig()


    for gen in range(pop_config.NB_GENERATIONS):

        print(f"Starting Generation {gen}")

        for i, ind in enumerate(population.individuals):

            evaluate_individual(ind, zoo, zoo_viz=0, net_viz=0, input_viz=0)

        population.evolve_generation()

    print("Evolution finished or aborted.")
    print(population.fitness_history)

if __name__ == "__main__":
    import time
    start_time = time.time()
    main()
    print("--- %s seconds ---" % (time.time() - start_time))
