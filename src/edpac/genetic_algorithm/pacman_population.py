"""
Population.py - Gestion de la population GA
"""

import os
import numpy as np
from typing import List, Callable, Tuple
from .individual import Individual
from ..zoo.pacman import Pacman
from .chromosome import Chromosome
from .population import Population
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
        self.individuals: List[Pacman] = [
            Pacman(pacman_config = MultiPacmanConfig(), chromo_config=chromosome_config)
            for _ in range(self.size)
        ]

    def init_new_individual(self, pacman_index, genes):

        #print(f"Saving old individual {pacman_index}")
        #print(self.individuals[pacman_index].save_stats())


        print(f"Init new individual {pacman_index}")
        self.individuals[pacman_index] = Pacman(pacman_config = MultiPacmanConfig(), chromo_config=self.chromosome_config)

        
    def __repr__(self):
        best_fit = self.best_individual.get_fitness() if self.best_individual else -1
        return f"Population(size={self.size}, gen={self.generation}, best_fit={best_fit:.3f})"
