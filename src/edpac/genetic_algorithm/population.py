"""
Population.py - Gestion de la population GA
"""

import os
import numpy as np
from typing import List, Callable, Tuple
from .individual import Individual
from .chromosome import Chromosome
from ..config.ga_config import (
    SelectionConfig, CrossoverConfig,
    MutationConfig, SelectionMode, MutationMode
)

from ..config.constants import *

from ..config.ga_config import PopulationConfig

from edpac.config.ga_config import ChromosomeConfig


from ..config.network_config import NetworkConfig
network_config = NetworkConfig()



class Population:
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


        np.random.seed(1)

        self.config = config or PopulationConfig()
        self.size = self.config.POPULATION_SIZE

        self.chromosome_config = chromosome_config or ChromosomeConfig()
        
        self.selection_config = selection_config or SelectionConfig()
        self.crossover_config = crossover_config or CrossoverConfig()
        self.mutation_config = mutation_config or MutationConfig()
#
#         # Créer population initiale
#         self.individuals: List[Individual] = [
#             Individual(config=chromosome_config)
#             for _ in range(self.size)
#         ]
        
        # Statistiques
        self.generation = 0
        self.best_individual = None
        self.fitness_history = []

        #self.set_chromosome_lengths()
        #print(self.lengths)
    
    def clean_population(self):

        for indiv in self.individuals :
            del indiv

        del self.individuals


    def evaluate(self, eval_func: Callable[[Individual], float]):
        """
        Évaluer toute la population
        
        Args:
            eval_func: Fonction d'évaluation
        """
        for ind in self.individuals:
            if not ind.fitness_evaluated:
                ind.evaluate(eval_func)
                print("Evaluate fitness for indiv", ind)
            else:
                print("fitness already evaluated for indiv", ind)
    
    def select_parent(self) -> Individual:
        """
        Sélectionner un parent
        
        Utilise le mode de sélection configuré
        """
        if self.selection_config.SELECTION_MODE == SelectionMode.TOURNAMENT:
            return self._tournament_selection()
        elif self.selection_config.SELECTION_MODE == SelectionMode.ROULETTE_WHEEL:
            return self._roulette_wheel_selection()
        else:
            return self._rank_selection()
    
    def _tournament_selection(self) -> Individual:
        """Sélection par tournoi"""
        tournament_size = self.selection_config.TOURNAMENT_SIZE
        
        # Sélectionner aléatoirement tournament_size individus
        candidates = np.random.choice(self.individuals, tournament_size, replace=False)
        
        # Retourner le meilleur
        return max(candidates, key=lambda x: x.get_fitness())
    
    def _roulette_wheel_selection(self) -> Individual:
        """Sélection par roulette (fitness proportionnelle)"""
        # Décaler les fitness pour éviter négatives
        fitnesses = np.array([ind.get_fitness() for ind in self.individuals])
        min_fitness = fitnesses.min()
        shifted_fitnesses = fitnesses - min_fitness + 1e-6
        
        # Calculer probabilités proportionnelles
        probs = shifted_fitnesses / shifted_fitnesses.sum()
        
        # Choisir selon probabilités
        idx = np.random.choice(len(self.individuals), p=probs)
        return self.individuals[idx]
    
    def _rank_selection(self) -> Individual:
        """Sélection par rang"""
        # Trier par fitness
        sorted_inds = sorted(self.individuals, key=lambda x: x.get_fitness(), reverse=True)
        
        # Probabilité basée sur rang
        ranks = np.arange(len(sorted_inds))
        probs = (len(sorted_inds) - ranks) / (len(sorted_inds) * (len(sorted_inds) + 1) / 2)
        
        idx = np.random.choice(len(sorted_inds), p=probs)
        return sorted_inds[idx]
    
    def crossover(self, parent1: Individual, parent2: Individual) -> Individual:
        """
        Crossover entre deux parents
        
        Args:
            parent1, parent2: Parents
            
        Returns:
            Offspring
        """
        genes1 = parent1.get_genes().copy()
        genes2 = parent2.get_genes().copy()


        if self.chromosome_config.VARIABLE_LENGTH_CHROMOSOME:

            if self.chromosome_config.RELATIVE_ENCODING:

                # One-point crossover
                crossover_point1 = np.random.choice(len(genes1),
                        1,
                        replace=False)

                crossover_point1 = int(crossover_point1[0] // self.chromosome_config.NB_GENES_EACH_PROJECTION)*self.chromosome_config.NB_GENES_EACH_PROJECTION

                crossover_point2 = np.random.choice(
                        int(float(len(genes2))/self.chromosome_config.NB_GENES_EACH_PROJECTION),
                        1,
                        replace=False)

                crossover_point2 = int(crossover_point2[0]*self.chromosome_config.NB_GENES_EACH_PROJECTION)


                # print(f"crossover_point1: {crossover_point1}")
                # print(f"crossover_point2: {crossover_point2}")

                part1 = genes1[:crossover_point1]
                part2 = genes2[crossover_point2:]

                # print("part1: ", part1.shape)
                #print("part2: ", part2.shape)

                offspring_genes = np.concatenate((part1, part2), axis = 0)
                print("offspring_genes: ", offspring_genes.shape)
                #print(offspring_genes)
            else:
                #TODO
                print("VARIABLE_LENGTH_CHROMOSOME=True and RELATIVE_ENCODING=False are not encoded yet")

        else:
            # One-point crossover
            crossover_point = np.random.choice(
                    len(genes1),
                    1,
                    replace=False)

            crossover_point = int(crossover_point[0])
            offspring_genes = genes1.copy()
            offspring_genes[crossover_point:] = genes2[crossover_point:]

            print("Offspring: ")
            print(offspring_genes)
            print("offspring_genes: ", offspring_genes.shape)

        indiv = Individual(self.chromosome_config, offspring_genes)
        return indiv
    
    def mutate(self, individual: Individual):
        """
        Muter un individu (in-place)
        
        Args:
            individual: Individu à muter
        """
        genes = individual.get_genes()

        if self.chromosome_config.RELATIVE_ENCODING:
            mask = np.array(np.random.rand(len(genes)) < self.mutation_config.MUTATION_RATE)
            genes[mask] = np.random.rand(len(genes))[mask]

        else:
            if self.chromosome_config.VARIABLE_LENGTH_CHROMOSOME:
                print("VARIABLE_LENGTH_CHROMOSOME=TRUE and RELATIVE_ENCODING=FALSE not implemented yet")

            else:
                print("Mutation")
                max_val = np.array([network_config.NB_IN_ASSEMBLIES, 2,
                                    network_config.NB_OUT_ASSEMBLIES]*self.chromosome_config.NB_PROJECTIONS_EACH_CHROMOSOME, dtype = int)

                mutation_rate = self.mutation_config.MUTATION_RATE

                mask = np.random.rand(len(genes)) < mutation_rate

                print("Nb Mutation", np.sum(mask == True))
                print("Before mutation: ", genes[mask])
                genes[mask] = np.random.randint(low = np.zeros(shape = max_val[mask].shape, dtype = int), high = max_val[mask])
                print("After mutation: ", genes[mask])


        # reinit
        individual.set_genes(genes)
        individual.fitness_evaluated = False
        individual.fitness = -float("inf")
    
    def set_chromosome_lengths(self):

        self.lengths = [indiv.genes.shape[0] for indiv in self.individuals if indiv != 0 ]

    def set_fitnesses(self, list_fitnesses):

        assert len(list_fitnesses) == len(self.individuals), "Error, Fitness length not matching individuals length"

        for indiv, fitness in zip(self.individuals, list_fitnesses):

            indiv.set_fitness(fitness)

    def set_indivual_ages(self):

        for indiv in self.individuals:

            indiv.set_age(self.generation)

    def get_best(self) -> Individual:
        """Retourner le meilleur individu"""
        return max(self.individuals, key=lambda x: x.get_fitness())
    
    def __repr__(self):
        best_fit = self.best_individual.get_fitness() if self.best_individual else -1
        return f"Population(size={self.size}, gen={self.generation}, best_fit={best_fit:.3f})"
