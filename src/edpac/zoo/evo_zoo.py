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
from edpac.zoo.pacman import Direction

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

                        #self.population.individuals[new_index].set_animal_nature(animal_nature)
                        return

            print("Could not find nearby empty position {x=} {y=} for new indiv {new_index}")
            print("Initing random_position")
            self.init_random_position(new_index)


    def generate_zoo_positions(self):

        for i in range(len(self.population.individuals)):

            if self.population.individuals[i]:
                self.init_random_position(i)

        print(self._grid)

    def init_empty_zoo(self):

        self.load_menagerie(menagerie_file= "menagerie.txt")
        self.load_screen(screen_file= "screen.empty")

        self.generate_zoo_positions()

    def _move_forward(self, pacman_index, verbose=0):
        """Calculates movement based on dir_body and updates grid."""
        # Map dir_body to coordinate changes
        #move_map = {Direction.UP: (0, -1), Direction.DOWN: (0, 1), Direction.LEFT: (-1, 0), Direction.RIGHT: (1, 0)}
        move_map = {Direction.DOWN: (0, -1), Direction.UP: (0, 1), Direction.LEFT: (-1, 0), Direction.RIGHT: (1, 0)}

        pac = self.population.individuals[pacman_index]

        dx, dy = move_map[pac.dir_body]

        new_x = pac.x + dx
        new_y = pac.y + dy

        target_char = self._in_grid(new_x, new_y)

        if not target_char:
            if verbose > 0:
                print(f"Pacman {pacman_index} could not move forward, {new_x=}, {new_y=} leads to error char={target_char}")
            return

        if target_char == 'X': # Not a wall
            if verbose > 0:
                print(f"Pacman {pacman_index} could not move forward, {new_x=}, {new_y=} is a wall")
            return

        # Update grid data: old position becomes a dot
        # if this a pacgum, increase life
        if target_char == ".":
            if verbose > 0:
                print(f"Pacman {pacman_index} Eating pacgum")
            pac.eat_pacgum()

        elif target_char != " ":

            index = char_to_index(target_char)
            animal = self.get_animal_from_index(index)

            if verbose > 0:
                print(f"Pacman {pacman_index } in contact with {target_char} ({index=})")

            if self.animals[animal]["danger"] == "1" and pac.get_animal_nature() == "-1":

                pac.eat_prey(self.population.individuals[index].get_life_points())

                if verbose > 0:
                    print(f"Pacman {pacman_index} Eating prey ", self.animals[animal]["name"])
                self.process_death(index)



            else:
                if verbose > 0:
                    print(f"Pacman {pacman_index} Same nature animal , cannot be eaten , we are no cannibals!")
                return

        # Old position is empty
        self._set_in_grid(pac.x, pac.y, ' ')

        # New position becomes Pacman
        self._set_in_grid(new_x, new_y, index_to_char(pacman_index))

        pac.set_position(new_x, new_y)

    def print_pacman_positions(self):

        for i,pacman in enumerate(self.population.individuals):
            print(f" pacman  Position {i}: ", pacman.get_position())

    def get_animal_from_index(self, index):
        return index % 2

    ########################################## online reproduction #######################################################
    def _check_available_individual_slot(self):

        avail = [i for i, pac in enumerate(self.population.individuals) if pac==0 ]

        if len(avail):
            return avail
        else:
            return -1

    def _find_first_avail(self, avail, target_danger):

        all_dangers = [self.animals[self.get_animal_from_index(index)]["danger"] for index in avail]

        for i, danger in enumerate(all_dangers):
            if danger == target_danger:
                return avail[i]
        return -1

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

        animal_nature = 0

        if parent1.get_animal_nature() == "-1" and parent2.get_animal_nature() == "-1":

            animal_nature = "-1"
            if parent1.pacman_config.MIN_LIFE_FOR_REPROD_PREDATOR <= parent1.get_life_points() and parent2.pacman_config.MIN_LIFE_FOR_REPROD_PREDATOR <= parent2.get_life_points():
                print(f"Enough life points to reproduce predators: {parent1.get_life_points()} {parent2.get_life_points()}")
                parent1.add_life_points(-int(parent1.pacman_config.MIN_LIFE_FOR_REPROD_PREDATOR // 2))
                parent2.add_life_points(-int(parent2.pacman_config.MIN_LIFE_FOR_REPROD_PREDATOR // 2))

            else:
                print(f"Not enough life points to reproduce predators {parent1.get_life_points()} {parent2.get_life_points()}")
                return False

        elif parent1.get_animal_nature() == "1" and parent2.get_animal_nature() == "1":

            animal_nature = "1"

            if parent1.pacman_config.MIN_LIFE_FOR_REPROD_PREY <= parent1.get_life_points() and parent2.pacman_config.MIN_LIFE_FOR_REPROD_PREY <= parent2.get_life_points():
                print(f"Enough life points to reproduce preys: {parent1.get_life_points()} {parent2.get_life_points()}")
                parent1.add_life_points(-int(parent1.pacman_config.MIN_LIFE_FOR_REPROD_PREY // 2))
                parent2.add_life_points(-int(parent2.pacman_config.MIN_LIFE_FOR_REPROD_PREY // 2))
            else:
                print(f"Not enough life points to reproduce preys {parent1.get_life_points()} {parent2.get_life_points()}")
                return False
        else:
            print(f"*Warning , animal_nature {parent1.get_animal_nature()} {parent1.get_animal_nature()} do not match")
            return False

        self.population.create_new_individual(new_index, parent1, parent2)

        return True

    def test_prey_reproduction(self, contact_index, pacman_index):
        # check if any slots are available
        avail = self._check_available_individual_slot()

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

        else:
            print(f"Could not compute _compute_online_reproduction {new_index=}, {contact_index=}, {pacman_index=} ")

    def test_predator_reproduction(self, contact_index, pacman_index):
        # check if any slots are available
        avail = self._check_available_individual_slot()

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

        else:
            print(f"Could not compute _compute_online_reproduction {new_index=}, {contact_index=}, {pacman_index=} ")

    def send_chromosome(self, new_index):
        print("Warning, should be implemented in inherited class")

