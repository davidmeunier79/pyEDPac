"""
Individual.py - Un individu dans la population GA

Un individu = Chromosome (génotype) + EvoNetwork (phénotype)
"""

import numpy as np
from typing import Optional
from copy import deepcopy
from ..config.ga_config import ChromosomeConfig
from .chromosome import Chromosome

class Individual(Chromosome):
    """
    Individu d'une population
    
    Contient:
    - Chromosome (génétique)
    - Réseau neuronal (phénotype)
    - Fitness (aptitude)
    """
    
    _individual_count = 0
    
    def __init__(self, config: ChromosomeConfig = None, genes: np.ndarray = None):
        """
        Créer un individu
        
        Args:
            chromosome: Chromosome de l'individu (si None, en génère un)
            config: Configuration
        """
        self.id = Individual._individual_count
        Individual._individual_count += 1
        
        super().__init__(config, genes)



        # Fitness
        self.fitness = -float('inf')  # Non évalué au départ
        self.fitness_evaluated = False
        
        # Statistiques
        self.age = 0
        self.birth_generation = 0

        self.stats = {}

        

    def evaluate(self, eval_func) -> float:
        """
        Évaluer l'individu

        Args:
            eval_func: Fonction d'évaluation(individual) -> fitness

        Returns:
            Fitness calculée
        """
        self.fitness = eval_func(self)
        self.fitness_evaluated = True
        return self.fitness

#
    def set_fitness(self, fitness_value) -> float:


        if not self.fitness_evaluated:

            self.fitness = fitness_value
            self.fitness_evaluated = True

        else:
            raise ValueError("Individual already evaluated")

    def get_fitness(self) -> float:
        """Retourner la fitness"""
        #print(self.fitness_evaluated)
        #print(self.fitness)

        if not self.fitness_evaluated:
            raise ValueError("Individual not evaluated yet")
        return self.fitness
    
    def is_better_than(self, other: 'Individual') -> bool:
        """Comparer avec un autre individu"""
        if not self.fitness_evaluated or not other.fitness_evaluated:
            raise ValueError("Both individuals must be evaluated")
        return self.fitness > other.fitness
    
    def clone(self) -> 'Individual':
        """Cloner l'individu"""
        new_ind = Individual(self.config, self.genes)
        new_ind.fitness = - float('inf')

        new_ind.fitness_evaluated = False

        return new_ind
    
    def set_age(self, new_age):
        """Fixer l'âge"""
        if self.age==0:
            self.age = new_age
    
    def __repr__(self):
        fitness_str = f"f={self.fitness:.3f}" if self.fitness_evaluated else "unevaluated"
        return f"Individual(id={self.id}, {fitness_str}, age={self.age})"
    
    def save_stats(self, indiv_path):

        import os
        import json

        self.stats["fitness"] = self.get_fitness()
        self.stats["nb_genes"] = len(self.genes)

        if indiv_path==0:
            indiv_path = os.path.abspath("")

        file_stats = os.path.join(indiv_path, "Stats_indiv.json")

        with open(file_stats, 'w+') as fp:
            json.dump(self.stats, fp, indent=4)


    @staticmethod
    def reset_count():
        """Réinitialiser le compteur"""
        Individual._individual_count = 0
