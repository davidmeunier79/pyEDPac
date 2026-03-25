import os
import gc

import sys
sys.path.insert(0, '../src')

# Force Qt to use the 'offscreen' platform (no window needed)
os.environ["QT_QPA_PLATFORM"] = "offscreen"

# Disable DBus warnings on clusters
os.environ["QT_NO_GLIB"] = "1"

from joblib import Parallel, delayed

from edpac.zoo.zoo import Zoo, Pacman

from edpac.genetic_algorithm.population import Population
from edpac.genetic_algorithm.chromosome import Chromosome

from edpac.ed_network.evo_network import EvoNetwork
from edpac.ed_network.ed_synapse import EDSynapse

from edpac.config.constants import MINIMAL_TIME

from edpac.config.ga_config import PopulationConfigTest, SelectionConfigTest
from edpac.config.ga_config import PopulationConfig

from edpac.tracer.network_tracer import NetworkTracer

def evaluate_individual(indiv, path_indiv):


    #################################### Zoo ######################################
    # 1. Initialize Data
    zoo = Zoo()
    zoo.load_menagerie(menagerie_file= "menagerie.txt")


    #################################### Pacamn ######################################
    pac = Pacman(indiv)
    zoo.set_pacman(pac)
    zoo.load_screen(screen_file="screen.0")

    ################################### EvoNetwork ################################

    net = EvoNetwork(indiv)

    print(net)

    spike_neuron_ids = net.initialize_inputs()

    network_tracer = NetworkTracer(net)
    network_tracer.record(0, spike_neuron_ids)

    while zoo.pacman.life_points > 0 :

        zoo.live_one_step()  # Update the model()

        zoo.test_pacman_contacts()

        # 1. Get sensory data from the world
        sensory_data = zoo.pacman.integrate_visio_outputs()
        #print(sensory_data)

        # 3 integrate to EDNetwork
        spike_neuron_ids = net.integrate_inputs(sensory_data)

        ### init wave loop
        current_time = EDSynapse.event_manager.get_time()

        # tracer
        network_tracer.record(current_time, spike_neuron_ids)

        net.init_output_patterns()

        while (EDSynapse.event_manager.get_time() - current_time) < MINIMAL_TIME:

            time_before = EDSynapse.event_manager.get_time()

            spike_neuron_ids = EDSynapse.event_manager.run_one_step()

            if len(spike_neuron_ids):
                network_tracer.record(time_before, spike_neuron_ids)

            if EDSynapse.event_manager.get_nb_events() == 0:
                print("No more events in event manager, breaking")
                zoo.pacman.life_points = -100
                break

        output_patterns = net.get_output_patterns()
        #print(output_patterns)


        zoo.pacman.integrate_motor_outputs(output_patterns)

        zoo.pacman.life_points = zoo.pacman.life_points -1


    print("After Loop")

    # saving spike traces
    network_tracer.plot(target_dir = path_indiv)

    # 5. Now we can finally return the value to the EA
    score = EDSynapse.event_manager.get_time()

    indiv.set_fitness(score)

    # saving chromosome
    indiv.save_genes(path_indiv)

    pac.save_stats(path_indiv)

    # 3. Explicitly delete heavy local references
    del net
    del indiv
    del pac

    EDSynapse.event_manager.reset()

    del EDSynapse.event_manager

    print(indiv)

    return score

def run_parallel_evolution(population, indiv_paths):
    # n_jobs=-1 uses all available cores
    # backend="multiprocessing" is safest for NumPy-heavy code
    results = Parallel(n_jobs=50, backend="multiprocessing")(
        delayed(evaluate_individual)(ind, path_indiv) for ind, path_indiv in zip(population.individuals, indiv_paths)
    )
    return results


def main():

    def create_indiv_path(population, gen):

        indiv_paths = []

        for i in range(len(population.individuals)):
            path_indiv = os.path.abspath(f"Gen_{gen}/Ind_{i}/")

            try:
                os.makedirs(path_indiv)
            except OSError as e:
                print(f"Error {e}")

            indiv_paths.append(path_indiv)

        return indiv_paths

    # Create objects
    #################################### Population ######################################
    #population = Population()
    population = Population(selection_config = SelectionConfigTest(), config = PopulationConfigTest())

    for gen in range(population.config.NB_GENERATIONS):

        print(f"Starting Generation {gen}")

        indiv_paths = create_indiv_path(population, gen)

        results = run_parallel_evolution(population, indiv_paths)
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
