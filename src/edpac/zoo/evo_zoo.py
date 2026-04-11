import multiprocessing as mp
import numpy as np
import random

import sys
sys.path.insert(0, '../src')


from edpac.config.constants import NB_VISIO_INPUTS, MINIMAL_TIME
from edpac.config.network_config import NetworkConfig
from edpac.config.ga_config import PopulationConfig

#from edpac.genetic_algorithm.population import Population

from .pacman_population import PacmanPopulation

from edpac.zoo.zoo import Zoo

from edpac.zoo.chars import char_to_index, index_to_char

# --- The Centralized Population ---
class EvoZoo(Zoo):
    def __init__(self, pop_config : PopulationConfig = None):

        self.pop_config = pop_config or PopulationConfig()
        self.population = PacmanPopulation(config=self.pop_config )
        super().__init__()

    def init_random_position(self, index):
            added = False

            while not added:

                pos_y = random.randrange(1, self.rows-2)
                pos_x = random.randrange(1, self.cols-2)

                #print(f"{pos_y=}, {pos_x=}")
                char = self._in_grid(pos_x, pos_y)
                if not char:
                    continue

                if char == '.' or char == ' ':

                    print(f"Setting position for pacman {index}: {pos_y, pos_x}")
                    self._set_in_grid(pos_x, pos_y, index_to_char(index))
                    animal = self.get_animal_from_index(index)

                    animal_nature = self.animals[animal]["danger"]
                    #
                    # if animal_nature == "1":
                    #     self.stats["nb_preys"] += 1
                    # elif animal_nature == "-1":
                    #     self.stats["nb_predators"] += 1

                    #self.population.individuals[index].set_animal_nature(animal_nature)
                    self.population.individuals[index].set_position(y=pos_y,x=pos_x)
                    added = True

    def init_nearby_position(self, new_index, parent1_index, parent2_index):

            parent1 = self.population.individuals[parent1_index]
            parent2 = self.population.individuals[parent2_index]

            assert parent1 and parent2, f"Issue with init_nearby_position, {parent1=} ,  {parent2=}"

            directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]

            for parent in [parent1, parent2]:

                x, y = parent.get_position()

                for dir_x, dir_y in directions:

                    char_contact = self._in_grid(x + dir_x, y + dir_y)
                    if not char_contact:
                        continue

                    if char_contact in (".", " ") :
                        print(f"Position of new_individual:  {x + dir_x} {y + dir_y}")
                        self.population.individuals[new_index].set_position(x + dir_x, y + dir_y)

                        self._set_in_grid(x + dir_x, y + dir_y, index_to_char(new_index))

                        animal = self.get_animal_from_index(new_index)
                        animal_nature = self.animals[animal]["danger"]
                        assert animal_nature == parent1.get_animal_nature() and animal_nature == parent2.get_animal_nature(), \
                            f"Error with {animal_nature=} and {parent1.get_animal_nature()} , {parent2.get_animal_nature()}"

                        self.population.individuals[new_index].set_animal_nature(animal_nature)
                        return

            print("Could not find nearby empty position {x=} {y=} for new indiv {new_index}")
            print("Initing random_position")
            self.init_random_position(new_index)


    def generate_zoo_positions(self):
        #
        # random_pos_x = np.random.randint(low = 1, high = self.rows-1, size = len(self.population.individuals))
        # random_pos_y = np.random.randint(low = 1, high = self.cols-1, size = len(self.population.individuals))
        #
        # print(random_pos_x, random_pos_y)

        for i in range(len(self.population.individuals)):

            if self.population.individuals[i]:
                self.init_random_position(i)

        print(self._grid)

    def init_empty_zoo(self):

        self.load_menagerie(menagerie_file= "menagerie.txt")
        self.load_screen(screen_file= "screen.empty")

        self.generate_zoo_positions()

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

    def compute_percept(self, pacman_index):

        pacman=self.population.individuals[pacman_index]

        if pacman == 0:
            print(f"Pacman {pacman_index} is empty, skipping")

            return -1

        #print(f"Position pacman {i}: ", pacman.get_position())

        input_percept = self.integrate_visio_outputs(pac= pacman)


        if all([percept is None for percept in input_percept]):

            #print(f"Pacman {i}: sending empty inputs")

            input_percepts = 1

        return input_percept


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

    # TODO
    def get_animal_from_index(self, index):
        return index % 2

#         assert 0 <= index < population.pop_config.POPULATION_SIZE
#
#         if  index < population.pop_config.INIT_PREY_POPULATION_SIZE
#             return 0
#         elif se

    def _find_first_avail(self, avail, target_danger):

        all_dangers = [self.animals[index % 2]["danger"] for index in avail]

        for i, danger in enumerate(all_dangers):
            if danger == target_danger:
                return avail[i]
        return -1

    def test_prey_reproduction(self, contact_index, pacman_index):
        # check if any slots are available
        avail = self.check_available_individual_slot()

        if avail == -1: # no available slot
            #print(f"No available slots for prey_reproduction {contact_index}, {pacman_index}, breaking")
            return

        new_index = self._find_first_avail(avail, target_danger = "1")

        if new_index == -1:
            #print("No available slots for prey_reproduction danger, breaking")
            return

        if self._compute_online_reproduction(new_index, contact_index, pacman_index):

            print(f"Prey {new_index=} available, building")
            #self.stats["nb_preys"] += 1
            #self.init_nearby_position(new_index, contact_index, pacman_index)
            self.init_random_position(new_index)

            self.send_chromosome(new_index)
            #self.population.send_init_input(new_index)

        else:
            print(f"Could not compute _compute_online_reproduction {new_index=}, {contact_index=}, {pacman_index=} ")

    def test_predator_reproduction(self, contact_index, pacman_index):
        # check if any slots are available
        avail = self.check_available_individual_slot()

        if avail == -1: # no available slot
            #print(f"No available slots for predator_reproduction {contact_index}, {pacman_index}, breaking")
            return

        new_index = self._find_first_avail(avail, target_danger = "-1")

        if new_index == -1:
            #print("No available slots for predator_reproduction danger, breaking")
            return

        if self._compute_online_reproduction(new_index, contact_index, pacman_index):
            print(f"Predator {new_index=} available, building")
            #self.stats["nb_predators"] += 1

            #self.init_nearby_position(new_index, contact_index, pacman_index)
            self.init_random_position(new_index)

            self.send_chromosome(new_index)
            #self.population.send_init_input(new_index)

        else:
            print(f"Could not compute _compute_online_reproduction {new_index=}, {contact_index=}, {pacman_index=} ")

    def _compute_online_reproduction(self, new_index, contact_index, pacman_index):

        # non empty parents
        if self.population.individuals[contact_index] == 0:
            print(f"Error: for reproduction, indiv {contact_index} should not be empty")
            return False

        parent1 = self.population.individuals[contact_index]

        if self.population.individuals[pacman_index] == 0:
            print(f"Error: for reproduction, indiv {pacman_index} should not be empty")
            return False

        parent2 = self.population.individuals[pacman_index]

        if parent1.get_animal_nature() == "-1" and parent2.get_animal_nature() == "-1":

            if parent1.pacman_config.MIN_LIFE_FOR_REPROD_PREDATOR <= parent1.get_life_points() and parent2.pacman_config.MIN_LIFE_FOR_REPROD_PREDATOR <= parent2.get_life_points():
                print(f"Enough life points to reproduce preys: {parent1.get_life_points()} {parent2.get_life_points()}")
                parent1.add_life_points(-int(parent1.pacman_config.MIN_LIFE_FOR_REPROD_PREDATOR // 2))
                parent2.add_life_points(-int(parent2.pacman_config.MIN_LIFE_FOR_REPROD_PREDATOR // 2))
                
            else:
                print(f"Not enough life points to reproduce predators{parent1.get_life_points()} {parent2.get_life_points()}")
                return False

        elif parent1.get_animal_nature() == "1" and parent2.get_animal_nature() == "1":

            if parent1.pacman_config.MIN_LIFE_FOR_REPROD_PREY <= parent1.get_life_points() and parent2.pacman_config.MIN_LIFE_FOR_REPROD_PREY <= parent2.get_life_points():
                print(f"Enough life points to reproduce preys: {parent1.get_life_points()} {parent2.get_life_points()}")
                parent1.add_life_points(-int(parent1.pacman_config.MIN_LIFE_FOR_REPROD_PREY // 2))
                parent2.add_life_points(-int(parent2.pacman_config.MIN_LIFE_FOR_REPROD_PREY // 2))
            else:
                print(f"Not enough life points to reproduce preys{parent1.get_life_points()} {parent2.get_life_points()}")
                return False
        else:
            print(f"*Warning , animal_nature {parent1.get_animal_nature()} {parent1.get_animal_nature()} do not match")
            return False

        # compute mix chromosome between two parents
        offspring = self.population.crossover(parent1, parent2)
        #print("After crossover, offspring = ", offspring.genes)

        # Muter
        self.population.mutate(offspring)
        #print("After mutation, offspring = ", offspring.genes)
        #print(f"{offspring.get_nb_genes()=}")

        self.population.init_new_individual(new_index = new_index, genes = offspring.get_genes())

        self.population.individuals[new_index].set_parents((parent1.id, parent2.id))

        return True


    def check_available_individual_slot(self):

        avail = [i for i, pac in enumerate(self.population.individuals) if pac==0 ]

        if len(avail):
            return avail
        else:
            return -1

    def send_chromosome(self, new_index):
        print("Warning, should be implemented in inherited class")

