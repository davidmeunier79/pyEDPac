"""
Population.py - Gestion de la population GA
"""

import os
import numpy as np
from typing import List, Callable, Tuple
#from .individual import Individual
from .pacman import Pacman
#from .chromosome import Chromosome
from ..genetic_algorithm.population import Population
from ..config.ga_config import (
    SelectionConfig, CrossoverConfig,
    MutationConfig, SelectionMode, MutationMode
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

        # Créer population initiale
        self.init_pacman_population(chromosome_config)

        self.set_chromosome_lengths()
        print(self.lengths)

    def init_pacman_population(self, chromosome_config):
        self.individuals = []

        while len(self.individuals) < self.config.POPULATION_SIZE:

            if len(self.individuals) < self.config.INIT_PREDATOR_POPULATION_SIZE:
                pac_predator = Pacman(pacman_config = MultiPacmanConfig(), chromo_config=chromosome_config)
                pac_predator.set_animal_nature("-1")
                self.individuals.append(pac_predator)

            elif len(self.individuals) < self.config.INIT_PREDATOR_POPULATION_SIZE + self.config.INIT_PREY_POPULATION_SIZE:
                pac_prey = Pacman(pacman_config = MultiPacmanConfig(), chromo_config=chromosome_config)
                pac_prey.set_animal_nature("1")
                self.individuals.append(pac_prey)

            else:
                self.individuals.append(0)

    def init_new_individual(self, pacman_index, genes):

        #print(f"Saving old individual {pacman_index}")
        #print(self.individuals[pacman_index].save_stats())


        print(f"Init new individual {pacman_index}")
        self.individuals[pacman_index] = Pacman(pacman_config = MultiPacmanConfig(), chromo_config=self.chromosome_config, genes=genes)
        self.generation +=1
        self.individuals[pacman_index].set_age(self.generation)

        
    def __repr__(self):
        best_fit = self.best_individual.get_fitness() if self.best_individual else -1
        return f"Population(size={self.size}, gen={self.generation}, best_fit={best_fit:.3f})"
