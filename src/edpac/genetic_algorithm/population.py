"""
Population.py - Gestion de la population GA
"""

import numpy as np
from typing import List, Callable, Tuple
from .individual import Individual
from .chromosome import Chromosome
from ..config.ga_config import (
    PopulationConfig, SelectionConfig, CrossoverConfig, 
    MutationConfig, SelectionMode, MutationMode
)

class Population:
    """Population d'individus"""
    
    def __init__(self, 
                 size: int,
                 chromosome_config,
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
        self.size = size
        self.chromosome_config = chromosome_config
        
        self.selection_config = selection_config or SelectionConfig()
        self.crossover_config = crossover_config or CrossoverConfig()
        self.mutation_config = mutation_config or MutationConfig()
        
        # Créer population initiale
        self.individuals: List[Individual] = [
            Individual(config=chromosome_config) 
            for _ in range(size)
        ]
        
        # Statistiques
        self.generation = 0
        self.best_individual = None
        self.fitness_history = []
    
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
        
        if self.crossover_config.UNIFORM_CROSSOVER:
            # Uniform crossover
            mask = np.random.rand(len(genes1)) < self.crossover_config.UNIFORM_CROSSOVER_RATIO
            offspring_genes = np.where(mask, genes1, genes2)
        else:
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
        
        chromosome = Chromosome(self.chromosome_config, offspring_genes)
        return Individual(chromosome, self.chromosome_config)
    
    def mutate(self, individual: Individual):
        """
        Muter un individu (in-place)
        
        Args:
            individual: Individu à muter
        """
        genes = individual.chromosome.get_genes()
        
        mutation_rate = self.mutation_config.MUTATION_RATE
        
        if self.mutation_config.MUTATION_MODE == MutationMode.GAUSSIAN:
            # Mutation gaussienne
            mask = np.random.rand(len(genes)) < mutation_rate
            genes[mask] += np.random.normal(0, self.mutation_config.GAUSSIAN_SIGMA, mask.sum())
        
        elif self.mutation_config.MUTATION_MODE == MutationMode.UNIFORM:
            # Mutation uniforme
            mask = np.random.rand(len(genes)) < mutation_rate
            genes[mask] += np.random.uniform(
                -self.mutation_config.UNIFORM_MAGNITUDE,
                self.mutation_config.UNIFORM_MAGNITUDE,
                mask.sum()
            )
        
        else:
            # Biased mutation
            mask = np.random.rand(len(genes)) < mutation_rate
            genes[mask] = np.random.rand(mask.sum())
        
        # Clamp to [0, 1]
        genes = np.clip(genes, 0.0, 1.0)
        
        individual.chromosome.set_genes(genes)
        individual.fitness_evaluated = False
    
    def evolve_generation(self, eval_func: Callable, elite_size: int = 10):
        """
        Générer la prochaine génération
        
        Args:
            eval_func: Fonction d'évaluation
            elite_size: Nombre d'élites à conserver
        """
        # Évaluer la population actuelle
        self.evaluate(eval_func)
        
        # Trouver les élites
        sorted_inds = sorted(
            self.individuals,
            key=lambda x: x.get_fitness(),
            reverse=True
        )
        
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
        
        # Créer nouvelle génération
        new_pop = [ind.clone() for ind in elite]  # Conserver élites
        
        # Générer offspring
        while len(new_pop) < self.size:
            if np.random.rand() < self.crossover_config.CROSSOVER_RATE:
                # Crossover
                parent1 = self.select_parent()
                parent2 = self.select_parent()
                offspring = self.crossover(parent1, parent2)
            else:
                # Mutation seule
                parent = self.select_parent()
                offspring = parent.clone()
            
            # Muter
            self.mutate(offspring)
            new_pop.append(offspring)
        
        # Remplacer population
        self.individuals = new_pop[:self.size]
        self.generation += 1

        return self.best_individual
    
    def get_best(self) -> Individual:
        """Retourner le meilleur individu"""
        return max(self.individuals, key=lambda x: x.get_fitness())
    
    def __repr__(self):
        best_fit = self.best_individual.get_fitness() if self.best_individual else -1
        return f"Population(size={self.size}, gen={self.generation}, best_fit={best_fit:.3f})"
