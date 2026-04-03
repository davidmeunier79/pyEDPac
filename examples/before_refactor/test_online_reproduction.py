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
from edpac.zoo.chars import index_to_char, char_to_index

from edpac.genetic_algorithm.population import Population
from edpac.genetic_algorithm.chromosome import Chromosome

from edpac.ed_network.evo_network import EvoNetwork
from edpac.ed_network.ed_synapse import EDSynapse

from edpac.config.constants import MINIMAL_TIME

from edpac.config.ga_config import PopulationConfigMultiTest, SelectionConfigTest

from edpac.tracer.network_tracer import NetworkTracer



from multipac.parallel.parallel_zoo import ParallelZoo

def main():


    # Create objects
    #################################### Zoo ######################################
    # 1. Initialize Data
    config = PopulationConfigMultiTest()

    config.POPULATION_SIZE = 10

    config.INIT_POPULATION_SIZE = 3

    zoo = ParallelZoo(config = config)

    zoo.load_menagerie(menagerie_file= "menagerie.txt")

    zoo.load_screen(screen_file="screen.empty")


    #zoo.init_empty_zoo()
    pac = zoo.population.individuals[0]
    pac.set_animal_nature("1")
    pac.set_position(10, 11)
    zoo.grid[11, 10] = index_to_char(0)


    pac = zoo.population.individuals[1]
    pac.set_animal_nature("-1")
    pac.set_position(5, 18)
    zoo.grid[18, 5] = index_to_char(1)


    pac = zoo.population.individuals[2]
    pac.set_animal_nature("1")
    pac.set_position(10, 12)
    zoo.grid[12, 10] = index_to_char(2)

    print(zoo.grid)

    zoo.population.deploy()

    zoo.test_pacman_contacts()


if __name__ == "__main__":
    import time
    start_time = time.time()
    main()
    print("--- %s seconds ---" % (time.time() - start_time))
