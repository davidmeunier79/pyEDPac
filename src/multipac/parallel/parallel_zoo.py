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

    def generate_zoo_positions(self):

        random_pos_x = np.random.randint(low = 1, high = self.rows-1, size = len(self.population.individuals))
        random_pos_y = np.random.randint(low = 1, high = self.cols-1, size = len(self.population.individuals))

        print(random_pos_x, random_pos_y)

        for i,pos in enumerate(zip(random_pos_x, random_pos_y)):

            print(pos)
            char = self.grid[pos].decode("utf-8")

            if char != 'X':

                print(f"Setting position for pacman {i}: {pos}")
                self.grid[pos] = int(i % 2) + 1
                self.population.individuals[i].set_animal_nature(self.animals[char]["danger"])
                self.population.individuals[i].set_position(pos[0], pos[1])

            else:
                print(f"Could not generate pacman {i}: {pos}")
        print(self.grid)

    def init_empty_zoo(self):


        self.load_menagerie(menagerie_file= "menagerie.txt")
        self.load_screen(screen_file= "screen.empty")

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

            input_pecept = self.integrate_visio_outputs(pac= pacman)
            print(input_pecept)
            input_percepts.append(input_pecept)

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


