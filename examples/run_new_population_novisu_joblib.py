import os
import gc

import sys
sys.path.insert(0, '../src')

from joblib import Parallel, delayed

from edpac.zoo.zoo import Zoo, Pacman

from edpac.genetic_algorithm.population import Population
from edpac.genetic_algorithm.chromosome import Chromosome

from edpac.ed_network.evo_network import EvoNetwork
from edpac.ed_network.ed_synapse import EDSynapse

from edpac.config.constants import MINIMAL_TIME

from edpac.config.ga_config import PopulationConfig

def evaluate_individual(indiv):


    #################################### Zoo ######################################
    # 1. Initialize Data
    zoo = Zoo()
    zoo.load_menagerie(menagerie_file= "menagerie.txt")


    #################################### Pacamn ######################################
    pac = Pacman(indiv)
    zoo.set_pacman(pac)
    zoo.load_screen(screen_file="screen.0")

    ################################### EvoNetwork ################################

    net = EvoNetwork(indiv.get_chromosome())
    net.initialize_inputs()

    print(net)

    while zoo.pacman.life_points > 0 :

        zoo.live_one_step()  # Update the model()

        zoo.test_pacman_contacts()

        # 1. Get sensory data from the world
        sensory_data = zoo.pacman.integrate_visio_outputs()
        #print(sensory_data)

        # 3 integrate to EDNetwork
        net.integrate_inputs(sensory_data)

        current_time = EDSynapse.event_manager.get_time()

        net.init_output_patterns()

        while (EDSynapse.event_manager.get_time() - current_time) < MINIMAL_TIME:

            #net_viz.display_empty_network()

            spike_neuron_ids = EDSynapse.event_manager.run_one_step()

            if EDSynapse.event_manager.get_nb_events() == 0:
                print("No more events in event manager, breaking")
                zoo.pacman.life_points = -100
                break

        output_patterns = net.get_output_patterns()
        #print(output_patterns)


        zoo.pacman.integrate_motor_outputs(output_patterns)

        zoo.pacman.life_points = zoo.pacman.life_points -1

    # 3. Explicitly delete heavy local references
    del net
    del pac

    #print("After Loop")

    # 5. Now we can finally return the value to the EA
    score = EDSynapse.event_manager.get_time()

    indiv.set_fitness(score)

    EDSynapse.event_manager.reset()

    del EDSynapse.event_manager

    print(indiv)

    return score

def run_parallel_evolution(population):
    # n_jobs=-1 uses all available cores
    # backend="multiprocessing" is safest for NumPy-heavy code
    results = Parallel(n_jobs=50, backend="multiprocessing")(
        delayed(evaluate_individual)(ind) for ind in population.individuals
    )
    return results


def main():

    # Create objects
    #################################### Population ######################################

    population = Population()
    pop_config = PopulationConfig()


    for gen in range(pop_config.NB_GENERATIONS):

        print(f"Starting Generation {gen}")

        results = run_parallel_evolution(population)
        print(results)

        population.set_fitnesses(results)
        population.evolve_generation()

    print("Evolution finished or aborted.")
    print(population.fitness_history)

if __name__ == "__main__":
    import time
    start_time = time.time()
    main()
    print("--- %s seconds ---" % (time.time() - start_time))
