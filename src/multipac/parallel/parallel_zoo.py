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

from edpac.zoo.chars import char_to_index, index_to_char

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

                pos_y = random.randrange(1, self.rows-2)
                pos_x = random.randrange(1, self.cols-2)

                #print(f"{pos_y=}, {pos_x=}")
                char = self.grid[pos_y, pos_x].decode("utf-8")

                if char == '.' or char == ' ':

                    print(f"Setting position for pacman {index}: {pos_y, pos_x}")
                    self.grid[pos_y, pos_x] = index_to_char(index)
                    animal = index % 2

                    animal_nature = self.animals[animal]["danger"]

                    if animal_nature == "1":
                        self.stats["nb_preys"] += 1
                    elif animal_nature == "-1":
                        self.stats["nb_predators"] += 1

                    self.population.individuals[index].set_animal_nature(animal_nature)
                    self.population.individuals[index].set_position(y=pos_y,x=pos_x)
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
        self.load_screen(screen_file= "screen.empty")

        self.generate_zoo_positions()

        self.population.deploy()

        self.population.distribute_chromosomes()

    def compute_zoo_interaction(self):

        input_percepts = []
        for i,pacman in enumerate(self.population.individuals):
            #print (i, pacman)
            if pacman == 0:
                #print(f"Pacman {i} is empty, skipping")
                input_percepts.append(-1)
                continue

            #print(f"Position pacman {i}: ", pacman.get_position())

            input_percept = self.integrate_visio_outputs(pac= pacman)

            #print([percept is None for percept in input_percept])
            #print("test all is None ", all([percept is None for percept in input_percept]))

            if all([percept is None for percept in input_percept]):

                #print(f"Pacman {i}: sending empty inputs")

                input_percepts.append(1)
            else:
                #print(input_pecept)
                input_percepts.append(input_percept)

        return input_percepts

    def print_pacman_positions(self):

        for i,pacman in enumerate(self.population.individuals):
            print(f" pacman  Position {i}: ", pacman.get_position())


    def compute_move_pos(self, move_pos):

        for pacman_index, pos in move_pos.items():
            pac = self.population.individuals[pacman_index]

            if pos == 1:
                #print(f"Individual {pacman_index} moving forward")
                self._move_forward(pacman_index)
            elif pos == -1:
                self.process_death(pacman_index)
#
    def _find_first_avail(self, avail, target_danger):

        all_dangers = [self.animals[new_index % 2]["danger"] for new_index in avail]

        for i, danger in enumerate(all_dangers):
            if danger == target_danger:
                return avail[i]
        return -1

    def test_prey_reproduction(self, contact_index, pacman_index):
        # check if any slots are available
        avail = self.check_available_individual_slot()

        if avail == -1: # no available slot
            print(f"No available slots for prey_reproduction {contact_index}, {pacman_index}, breaking")
            return

        new_index = self._find_first_avail(avail, target_danger = "1")

        if new_index == -1:
            print("No available slots for prey_reproduction danger, breaking")
            return

        print(f"Prey {new_index=} available, building")
        if self._compute_online_reproduction(new_index, contact_index, pacman_index):
            #self.stats["nb_preys"] += 1
            self.init_random_position(new_index)
            self.population.send_init_input(new_index)
            self.nb_deads -= 1

        print(f"******************** {self.nb_deads=} ***********************")


    def test_predator_reproduction(self, contact_index, pacman_index):
        # check if any slots are available
        avail = self.check_available_individual_slot()

        if avail == -1: # no available slot
            print(f"No available slots for predator_reproduction {contact_index}, {pacman_index}, breaking")
            return

        new_index = self._find_first_avail(avail, target_danger = "-1")

        if new_index == -1:
            print("No available slots for predator_reproduction danger, breaking")
            return

        print(f"Predator {new_index=} available, building")
        if self._compute_online_reproduction(new_index, contact_index, pacman_index):
            #self.stats["nb_predators"] += 1
            self.init_random_position(new_index)

            self.population.send_chromosome(new_index)

            self.population.send_init_input(new_index)
            self.nb_deads -= 1

        print(f"******************** {self.nb_deads=} ***********************")

    def _compute_online_reproduction(self, new_index, contact_index, pacman_index):

        if self.population.individuals[contact_index] == 0:
            return False

        parent1 = self.population.individuals[contact_index]

        if self.population.individuals[pacman_index] == 0:
            return False

        parent2 = self.population.individuals[pacman_index]

        # compute mix chromosome between two parents
        offspring = self.population.crossover(parent1, parent2)

        # Muter
        self.population.mutate(offspring)
        #print(f"{offspring.get_nb_genes()=}")

        self.population.init_new_individual(new_index, offspring.get_genes())

        return True


    def check_available_individual_slot(self):

        avail = [i for i, pac in enumerate(self.population.individuals) if pac==0 ]

        if len(avail):
            return avail
        else:
            return -1




