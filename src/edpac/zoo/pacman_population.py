"""
Population.py - Gestion de la population GA
"""

import os
import json

import numpy as np
from typing import List, Callable, Tuple
#from .individual import Individual
from .pacman import Pacman
#from .chromosome import Chromosome
from ..genetic_algorithm.population import Population
from ..config.ga_config import (
    SelectionConfig, CrossoverConfig,
    MutationConfig
)

from ..config.constants import *

from ..config.ga_config import PopulationConfig

from edpac.config.ga_config import ChromosomeConfig

from edpac.config.zoo_config import MultiPacmanConfig



class PacmanPopulation(Population):
    """Population d'individus"""
    
    def __init__(self,
                 config: PopulationConfig = None,
                 chromosome_config = None,
                 selection_config: SelectionConfig = None,
                 crossover_config: CrossoverConfig = None,
                 mutation_config: MutationConfig = None):
        """
        Créer une population
        
        Args:
            size: Taille de la population
            chromosome_config: Configuration chromosomale
            selection_config: Configuration de sélection
            crossover_config: Configuration de crossover
            mutation_config: Configuration de mutation
        """

        super().__init__(config,
                 chromosome_config,
                 selection_config,
                 crossover_config,
                 mutation_config)

        self.dead_individuals = {}

        self.nb_preys = 0
        self.nb_predators = 0

        # Créer population initiale
        self.init_pacman_population(chromosome_config)

        self.set_chromosome_lengths()
        print(self.lengths)

    def init_pacman_population(self, chromosome_config):
        self.individuals = []

        while len(self.individuals) < self.config.POPULATION_SIZE:
            if len(self.individuals) % 2 == 1:
                if self.nb_preys < self.config.INIT_PREDATOR_POPULATION_SIZE:
                    pac_prey = Pacman(pacman_config = MultiPacmanConfig(), chromo_config=chromosome_config)
                    pac_prey.set_age(self.generation)
                    pac_prey.set_animal_nature("-1")
                    self.individuals.append(pac_prey)

                    self.nb_preys += 1
                else:
                    self.individuals.append(0)

            else:
                if self.nb_predators < self.config.INIT_PREY_POPULATION_SIZE:
                    pac_predator = Pacman(pacman_config = MultiPacmanConfig(), chromo_config=chromosome_config)
                    pac_predator.set_animal_nature("1")
                    pac_predator.set_age(self.generation)
                    self.individuals.append(pac_predator)
                    self.nb_predators += 1
                else:
                    self.individuals.append(0)

    def store_dead_individual(self,  pac : Pacman):

        if pac.get_age() in self.dead_individuals.keys():
            self.dead_individuals[pac.get_age()].append(pac.to_dict())
        else:
            self.dead_individuals[pac.get_age()] = [pac.to_dict()]

    def save_individuals(self, stats_path):
        print(self.dead_individuals)

        # 5. Save to JSON
        output_file = os.path.join(stats_path , "all_individuals.json")

        with open(output_file, 'w') as f:
            json.dump(self.dead_individuals, f, indent=4)

    ################################# online reproduction ###########################################
    def create_new_individual(self, new_index, parent1, parent2):

        assert parent1.get_animal_nature() == parent2.get_animal_nature(), \
            f"Error , different animal natures for parents: {parent1.get_animal_nature()} {parent2.get_animal_nature() }"

        # getting animal_nature
        animal_nature = parent1.get_animal_nature()

        # compute mix chromosome between two parents
        offspring = self.crossover(parent1, parent2)
        #print("After crossover, offspring = ", offspring.genes)

        # Muter
        self.mutate(offspring)
        #print("After mutation, offspring = ", offspring.genes)
        #print(f"{offspring.get_nb_genes()=}")

        self.init_new_individual(new_index = new_index, genes = offspring.get_genes())

        self.individuals[new_index].set_animal_nature(animal_nature)
        self.individuals[new_index].set_parents((parent1.id, parent2.id))


    def init_new_individual(self, new_index, genes):

        #print(f"Saving old individual {new_index}")
        #print(self.individuals[new_index].save_stats())


        print(f"Init new individual {new_index}")
        self.individuals[new_index] = Pacman(pacman_config = MultiPacmanConfig(), chromo_config=self.chromosome_config, genes=genes)
        self.generation +=1
        self.individuals[new_index].set_age(self.generation)

        
    def __repr__(self):
        best_fit = self.best_individual.get_fitness() if self.best_individual else -1
        return f"Population(size={self.size}, gen={self.generation}, best_fit={best_fit:.3f})"
