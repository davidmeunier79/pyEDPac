import multiprocessing as mp
import numpy as np
import random

import sys
sys.path.insert(0, '../src')


from edpac.config.constants import NB_VISIO_INPUTS, MINIMAL_TIME
from edpac.config.network_config import NetworkConfig
from edpac.config.ga_config import PopulationConfig

from edpac.genetic_algorithm.population import Population

from multipac.parallel.parallel_network import worker_loop

from multipac.parallel.parallel_population import ParallelPopulation

from edpac.zoo.zoo import Zoo

# --- The Centralized Population ---
class ParallelZoo(Zoo):
    def __init__(self, config : PopulationConfig = None):

        self.config = config or PopulationConfig()
        self.population = ParallelPopulation(pop_config = self.config )
        super().__init__()

        self.stats = {"nb_predators": 0, "nb_preys" : 0}

    def init_random_position(self, index):
            added = False

            while not added:

                pos_x = random.randrange(1, self.rows-1)
                pos_y = random.randrange(1, self.cols-1)

                print(f"{pos_x=}, {pos_y=}")
                char = self.grid[pos_x, pos_y].decode("utf-8")

                if char == '.':

                    print(f"Setting position for pacman {index}: {pos_x, pos_y}")
                    self.grid[pos_x, pos_y] = index
                    animal = index % 2
                    animal_nature = self.animals[animal]["danger"]

                    if animal_nature == "1":
                        self.stats["nb_preys"] += 1
                    elif animal_nature == "-1":
                        self.stats["nb_predators"] += 1

                    self.population.individuals[index].set_animal_nature(animal_nature)
                    self.population.individuals[index].set_position(pos_x, pos_y)
                    added = True

    def generate_zoo_positions(self):
        #
        # random_pos_x = np.random.randint(low = 1, high = self.rows-1, size = len(self.population.individuals))
        # random_pos_y = np.random.randint(low = 1, high = self.cols-1, size = len(self.population.individuals))
        #
        # print(random_pos_x, random_pos_y)

        for i in range(len(self.population.individuals)):

            self.init_random_position(i)

        print(self.grid)

    def init_empty_zoo(self):


        self.load_menagerie(menagerie_file= "menagerie.txt")
        self.load_screen(screen_file= "miniscreen.empty")

        self.generate_zoo_positions()

        self.population.deploy()

        self.population.distribute_chromosomes()

    def compute_zoo_interaction(self):

        input_percepts = []
        for i,pacman in enumerate(self.population.individuals):
            print (i, pacman)
            if pacman == 0:
                print(f"Pacman {i} is empty, skipping")
                input_percepts.append(-1)
                continue

            print(f"Position pacman {i}: ", pacman.get_position())

            input_percept = self.integrate_visio_outputs(pac= pacman)

            #print([percept is None for percept in input_percept])
            print("test all is None ", all([percept is None for percept in input_percept]))

            if all([percept is None for percept in input_percept]):

                print(f"Pacman {i}: sending empty inputs")

                input_percepts.append(1)
            else:
                #print(input_pecept)
                input_percepts.append(input_percept)

        return input_percepts

    def init_new_individual(self,pacman_index):

        self.population.init_new_individual(pacman_index)

    def print_pacman_positions(self):

        for i,pacman in enumerate(self.population.individuals):
            print(f" pacman  Position {i}: ", pacman.get_position())

    def compute_move_pos(self, move_pos):

        count_death = 0

        for pacman_index, pos in move_pos.items():
            #pac = self.population.individuals[pacman_index]

            if pos == 1:
                print(f"Individual {pacman_index} moving forward")
                self._move_forward(pacman_index)
            elif pos == -1:

                print(f"Individual {pacman_index} is dead")
                # dealing with death signal
                #self.init_new_individual(pacman_index)

                self.process_death(pacman_index)

                count_death += 1
#
#     def run_population(self):
#
#         print("In run_population")
#         self.population.initialize_all_inputs()
#
#         MAX_TIME = 10000
#         break_comp = True
#
#         while break_comp and MAX_TIME>0:
#             print(MAX_TIME)
#             input_percepts = self.compute_zoo_interaction()
#             print(f"{input_percepts=}")
#             #print(self.grid)
#             move_pos = self.population.run_one_step(input_percepts)
#             print(f"{move_pos=}")
#
#             self.compute_move_pos(move_pos)
#             print(f"{break_comp=}")
#             #print(self.grid)
#
#             #
#             # if all(self.population.individuals) == False:
#             #     print("Breaking")
#             #
#             #     break_comp = False
#             #     break
#             MAX_TIME -= 1
#
#         print("In shutting_down")
#         self.population.shutdown()
#
#

    def test_prey_reproduction(self, contact_index, pacman_index):
        # check if any slots are available
        new_index = self.check_available_individual_slot()

        if new_index == -1: # no available slot
            return

        if self.animals[new_index % 2]["danger"] == "-1": # predator for new index, break
            return

        print(f"Prey {new_index=} available, building")
        self._compute_online_reproduction(new_index, contact_index, pacman_index)
        #self.stats["nb_preys"] += 1

        self.init_random_position(new_index)

    def test_predator_reproduction(self, contact_index, pacman_index):
        # check if any slots are available
        new_index = self.check_available_individual_slot()

        if new_index == -1: # no available slot
            return

        if self.animals[new_index % 2]["danger"] == "1": # prey for new index, break
            return

        print(f"Predator {new_index=} available, building")
        self._compute_online_reproduction(new_index, contact_index, pacman_index)
        #self.stats["nb_predators"] += 1

        self.init_random_position(new_index)

    def _compute_online_reproduction(self, new_index, contact_index, pacman_index):

        if self.population.individuals[contact_index] == 0:
            return

        parent1 = self.population.individuals[contact_index]

        if self.population.individuals[pacman_index] == 0:
            return

        parent2 = self.population.individuals[pacman_index]

        # compute mix chromosome between two parents
        offspring = self.population.crossover(parent1, parent2)

        # Muter
        self.population.mutate(offspring)
        print(offspring.nb_genes.shape)

        self.population.individuals[new_index] = offspring


    def check_available_individual_slot(self):

        for i, pac in enumerate(self.population.individuals):
            if pac == 0:
                return i
        return -1




