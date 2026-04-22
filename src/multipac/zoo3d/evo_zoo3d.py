import multiprocessing as mp
import numpy as np
import random

import sys
sys.path.insert(0, '../src')


from edpac.config.constants import AREA_SIZE
from edpac.config.network_config import NetworkConfig
from edpac.config.ga_config import PopulationConfig

#from edpac.genetic_algorithm.population import Population

from edpac.zoo.pacman_population import PacmanPopulation

from edpac.zoo.pacman import Direction

from edpac.zoo.chars import char_to_index, index_to_char

# --- The Centralized Population ---
class EvoZoo3D():
    def __init__(self, pop_config : PopulationConfig = None):

        self.pop_config = pop_config or PopulationConfig()
        self.population = PacmanPopulation(config=self.pop_config )
        super().__init__()


        self.stats = {"time": [] , "nb_predators": [], "nb_preys" : [], "mean_predator_fitness" : [], "mean_prey_fitness": [], "generation" : [], "nb_deads": [], "nb_added_pacgums": []}


    def init_random_position3d(self, index):
        added = False

        while not added:

            pos_y = random.randrange(-AREA_SIZE//2 + 1, AREA_SIZE//2 -1)
            pos_x = random.randrange(-AREA_SIZE//2 + 1, AREA_SIZE//2 -1)

            #TODO
            #test for collision with already present agents

            print(f"Setting position for pacman {index}: {pos_y, pos_x}")

            #self.population.individuals[index].set_animal_nature(animal_nature)
            self.population.individuals[index].set_position(y=pos_y,x=pos_x)
            added = True


    def init_3D_zoo(self):

        for i in range(len(self.population.individuals)):

            if self.population.individuals[i]:
                self.init_random_position3d(i)

    def init_stats(self):

        self.stats["time"].append(0)
        self.stats["nb_predators"].append(0)
        self.stats["nb_preys"].append(0)
        self.stats["mean_predator_fitness"].append(0)
        self.stats["mean_prey_fitness"].append(0)

        self.stats["generation"].append(0)
        self.stats["nb_deads"].append(0)
        self.stats["nb_added_pacgums"].append(0)

    def save_stats(self, indiv_path=0):

        import json
        import os
        import pandas as pd

        if indiv_path == 0:
            indiv_path = os.path.abspath("")
        else:
            try:
                os.makedirs(os.path.abspath(indiv_path))
            except OSError:
                print(f"{os.path.abspath(indiv_path)} already exists")

        file_stats = os.path.join(indiv_path, f"Stats_evo.csv")

        df = pd.DataFrame(self.stats)
        df = df.set_index("time")

        df.to_csv(file_stats , header = True)


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
            self._send_chromosome(new_index)

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
            self._send_chromosome(new_index)

        else:
            print(f"Could not compute _compute_online_reproduction {new_index=}, {contact_index=}, {pacman_index=} ")


    ############################################ general population moves (test)
    def all_move_forward(self, turn_dir = 1):
        for pacman_index, pac in enumerate(self.population.individuals):
            #print(pac)
            if pac==0:
                continue

            self._move_forward(pacman_index)

    def turn_all_body(self, turn_dir = 1):
        for pacman_index, pac in enumerate(self.population.individuals):
            #print(pac)
            if pac == 0:
                continue

            pac.dir_body = pac._get_turn(pac.dir_body, turn_dir)


    def turn_all_heads(self, turn_dir = 1):
        for pacman_index, pac in enumerate(self.population.individuals):
            #print(pac)
            if pac==0:
                continue

            pac.dir_head = pac._get_turn(pac.dir_head, turn_dir)


    ############################################ stats

    def _compute_all_stats(self, verbose=0):

        for i, pac in enumerate(self.population.individuals):
            # poll(timeout) checks if data is waiting
            # timeout=0 makes it an instantaneous check

            if pac == 0:

                if verbose > 0:
                    print(f"[ParallelZoo] Worker {i} is empty, continue")
                continue


            if verbose > 0:
                print(f"[ParallelZoo] Worker {i} updating stats")

            pac.fitness = pac.get_life_points()
            pac.fitness_evaluated = True

            if pac.get_animal_nature() == "-1":
                self.stats["mean_predator_fitness"][-1] += pac.get_fitness()
                self.stats["nb_predators"][-1] +=1
            elif pac.get_animal_nature() == "1":
                self.stats["mean_prey_fitness"][-1] += pac.get_fitness()
                self.stats["nb_preys"][-1] +=1

            # naturally losing life each time points
            pac.add_life_points(-1)

            if pac.get_life_points() < 0:
                #self.init_new_individual(pacman_index)
                self.process_death(i)

    ################################# called here but implemented in ParallelZoo ############################
    def _send_death_signal(self, pacman_index):
        print("Error, should be implemented in inherited class")

    def _send_chromosome(self, new_index):
        print("Warning, should be implemented in inherited class")

