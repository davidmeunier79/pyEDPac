"""
Population.py - Gestion de la population GA
"""

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

pop_config = PopulationConfig()


class Population:
    """Population d'individus"""
    
    def __init__(self,
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
        self.size = pop_config.POPULATION_SIZE

        self.chromosome_config = chromosome_config or ChromosomeConfig()
        
        self.selection_config = selection_config or SelectionConfig()
        self.crossover_config = crossover_config or CrossoverConfig()
        self.mutation_config = mutation_config or MutationConfig()
        
        # Créer population initiale
        self.individuals: List[Individual] = [
            Individual(config=chromosome_config) 
            for _ in range(self.size)
        ]
        
        # Statistiques
        self.generation = 0
        self.best_individual = None
        self.fitness_history = []

        self.previous_populations = {}
    
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
                #print("Evaluate fitness for indiv", ind)
                ind.evaluate(eval_func)
            #else:
                #print("fitness already evaluated for indiv", ind)
    
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
        genes1 = parent1.chromosome.get_genes().copy()
        genes2 = parent2.chromosome.get_genes().copy()

        # One-point or multi-point crossover
        crossover_points = np.sort(
            np.random.choice(
                len(genes1),
                self.crossover_config.CROSSOVER_POINTS,
                replace=False
            )
        )

        offspring_genes = genes1.copy()
        for i, point in enumerate(crossover_points):
            if i % 2 == 1:
                offspring_genes[point:] = genes2[point:]
            else:
                offspring_genes[point:] = genes1[point:]

#
#         print("Offspring: ")
#         print(offspring_genes)

        chromosome = Chromosome(self.chromosome_config, offspring_genes)
        return Individual(chromosome)
    
    def mutate(self, individual: Individual):
        """
        Muter un individu (in-place)
        
        Args:
            individual: Individu à muter
        """
        genes = individual.chromosome.get_genes()
        
        max_val = np.array([NB_IN_ASSEMBLIES, 2, NB_OUT_ASSEMBLIES]*self.chromosome_config.NB_PROJECTIONS_EACH_CHROMOSOME, dtype = int)

        mutation_rate = self.mutation_config.MUTATION_RATE
        
        mask = np.random.rand(len(genes)) < mutation_rate
        #print("Mask mutation: ", mask)
        genes[mask] = np.random.randint(low = np.zeros(shape = max_val[mask].shape, dtype = int), high = max_val[mask])
        #print("Genes after mutation: ", genes)

        # Clamp to [0, 1]
        #genes = np.clip(genes, 0.0, 1.0)
        
        individual.chromosome.set_genes(genes)
        individual.fitness_evaluated = False
        individual.fitness = -float("inf")
    
    def evolve_generation(self):
        """
        Générer la prochaine génération
        
        Args:
            eval_func: Fonction d'évaluation
            elite_size: Nombre d'élites à conserver
        """
        # Évaluer la population actuelle
        #self.evaluate(eval_func)
#
#         for indiv in self.individuals:
#             print(indiv.id)
#             print(indiv.get_fitness())

        # Trouver les élites
        sorted_inds = sorted(
            self.individuals,
            key=lambda x: x.get_fitness(),
            reverse=True
        )
        
        print("******************* After gen ", self.generation)
        print(sorted_inds)

        elite_size = pop_config.ELITE_SIZE

        elite = sorted_inds[:elite_size]
        self.best_individual = elite[0]
        
        # Statistiques
        fitnesses = [ind.get_fitness() for ind in self.individuals]
        #print(fitnesses)

        self.fitness_history.append({
            'generation': self.generation,
            'best': max(fitnesses),
            'worst': min(fitnesses),
            'mean': np.mean(fitnesses),
            'std': np.std(fitnesses)
        })
        
        print(self.fitness_history)

        # Créer nouvelle génération

        new_pop = [ind.clone() for ind in elite]  # Conserver élites
        
        # Générer offspring
        while len(new_pop) < self.size:
            if np.random.rand() < self.crossover_config.CROSSOVER_RATE:
                print("Crossing Over")
                # Crossover
                parent1 = self.select_parent()
                parent2 = self.select_parent()
                offspring = self.crossover(parent1, parent2)
            else:
                print("No Crossing Over")
                # Mutation seule
                parent = self.select_parent()
                offspring = parent.clone()
            
            # Muter
            self.mutate(offspring)

            #print(offspring)

            new_pop.append(offspring)
        
        # Remplacer population
        #self.clean_population()

        #print(new_pop)

        self.previous_populations[self.generation] = self.individuals
        self.individuals = new_pop
        self.generation += 1
        self.set_indivual_ages()

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
