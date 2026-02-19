"""
Individual.py - Un individu dans la population GA

Un individu = Chromosome (génotype) + EvoNetwork (phénotype)
"""

import numpy as np
from typing import Optional
from copy import deepcopy
from ..config.ga_config import ChromosomeConfig
from .chromosome import Chromosome

class Individual:
    """
    Individu d'une population
    
    Contient:
    - Chromosome (génétique)
    - Réseau neuronal (phénotype)
    - Fitness (aptitude)
    """
    
    _individual_count = 0
    
    def __init__(self, chromosome: Chromosome = None, config: ChromosomeConfig = None):
        """
        Créer un individu
        
        Args:
            chromosome: Chromosome de l'individu (si None, en génère un)
            config: Configuration
        """
        self.id = Individual._individual_count
        Individual._individual_count += 1
        
        self.config = config or ChromosomeConfig()
        
        if chromosome is None:
            self.chromosome = Chromosome(self.config)
        else:
            self.chromosome = chromosome
        
        # Fitness
        self.fitness = -float('inf')  # Non évalué au départ
        self.fitness_evaluated = False
        
        # Statistiques
        self.age = 0
        self.birth_generation = 0
        
        # Réseau (sera créé lors de l'évaluation)
        self.network = None
    
    def set_chromosome(self, chromosome: Chromosome):
        """Définir le chromosome"""
        self.chromosome = chromosome
        self.fitness_evaluated = False
        self.fitness = -float('inf')
    
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
        new_ind = Individual(self.chromosome.clone(), self.config)
        new_ind.fitness = self.fitness
        new_ind.fitness_evaluated = self.fitness_evaluated
        return new_ind
    
    def increase_age(self):
        """Incrémenter l'âge"""
        self.age += 1
    
    def __repr__(self):
        fitness_str = f"f={self.fitness:.3f}" if self.fitness_evaluated else "unevaluated"
        return f"Individual(id={self.id}, {fitness_str}, age={self.age})"
    
    @staticmethod
    def reset_count():
        """Réinitialiser le compteur"""
        Individual._individual_count = 0
