"""
ga_training.py

Exemple d'utilisation du Genetic Algorithm
"""

import sys
sys.path.insert(0, '../src')
import random

#from edpac.genetic_algorithm.ga import GeneticAlgorithm
from edpac.genetic_algorithm.individual import Individual
from edpac.config.ga_config import (ChromosomeConfig, PopulationConfig, MutationConfig,
    CrossoverConfig, SelectionConfig, SelectionMode
)

"""
GA.py - Algorithme Génétique principal

Orchestrate l'évolution de la population
"""

import numpy as np
import time

from typing import Callable, List, Dict, Optional
import json
from datetime import datetime
from pathlib import Path

from edpac.genetic_algorithm.population import Population
from edpac.genetic_algorithm.individual import Individual


from dataclasses import dataclass, field

@dataclass
class GAConfig:
    """Configuration globale GA"""
    chromosome_config: ChromosomeConfig = field(default_factory=ChromosomeConfig)
    population_config: PopulationConfig = field(default_factory=PopulationConfig)
    selection_config: SelectionConfig = field(default_factory=SelectionConfig)
    crossover_config: CrossoverConfig = field(default_factory=CrossoverConfig)
    mutation_config: MutationConfig = field(default_factory=MutationConfig)

    # Général
    SEED: int = 42
    VERBOSE: bool = False
    SAVE_STATS: bool = True

    def validate(self):
        """Valider la configuration"""
        assert self.population_config.POPULATION_SIZE > 0
        assert self.population_config.ELITE_SIZE < self.population_config.POPULATION_SIZE
        assert 0 < self.selection_config.TOURNAMENT_SIZE < self.population_config.POPULATION_SIZE
        assert 0 <= self.crossover_config.CROSSOVER_RATE <= 1.0
        assert 0 <= self.mutation_config.MUTATION_RATE <= 1.0

class GeneticAlgorithm:
    """
    Algorithme Génétique pour l'évolution du réseau neuronal
    """

    def __init__(self, config: GAConfig, eval_func: Callable):
        """
        Initialiser l'GA

        Args:
            config: Configuration GA
            eval_func: Fonction d'évaluation (Individual -> fitness)
        """
        config.validate()
        self.config = config
        self.eval_func = eval_func

        # Seed aléatoire
        np.random.seed(config.SEED)
        Individual.reset_count()

        # Créer population
        self.population = Population(
            chromosome_config=config.chromosome_config,
            selection_config=config.selection_config,
            crossover_config=config.crossover_config,
            mutation_config=config.mutation_config
        )

        # Historique
        self.best_individuals: List[Individual] = []
        self.evolution_stats: List[Dict] = []

    def run(self, num_generations: Optional[int] = None) -> Individual:
        """
        Lancer l'algorithme génétique

        Args:
            num_generations: Nombre de générations (si None, utilise config)

        Returns:
            Meilleur individu trouvé
        """
        if num_generations is None:
            num_generations = self.config.population_config.NB_GENERATIONS

        if self.config.VERBOSE:
            print(f"Starting GA: {num_generations} generations, pop_size={self.population.size}")
            print(f"Mutation rate: {self.config.mutation_config.MUTATION_RATE}")
            print(f"Crossover rate: {self.config.crossover_config.CROSSOVER_RATE}")

        # Évaluer la population initiale
        for gen in range(num_generations):
            #
            self.population.evaluate(self.eval_func)
            print("After evaluation ", gen)

            # Évoluer une génération
            best = self.population.evolve_generation()

            # Enregistrer le meilleur
            #best = self.population.get_best()
            self.best_individuals.append(best.clone())

            # Stats
            stats = self.population.fitness_history[-1]
            self.evolution_stats.append(stats)

            if self.config.VERBOSE and (gen + 1) % 10 == 0:
                print(f"Gen {gen+1}/{num_generations}: "
                      f"best={stats['best']:.3f}, "
                      f"mean={stats['mean']:.3f}, "
                      f"std={stats['std']:.3f}")


            time.sleep(3.0)

        if self.config.VERBOSE:
            print(f"GA completed!")
            print(f"Best fitness: {self.best_individuals[-1].get_fitness():.3f}")

        return self.best_individuals[-1]

    def get_best_individual(self) -> Individual:
        """Retourner le meilleur individu trouvé"""
        if not self.best_individuals:
            return self.population.get_best()

        return max(self.best_individuals, key=lambda x: x.get_fitness())

    def get_convergence_curve(self) -> Dict[str, List]:
        """Retourner la courbe de convergence"""
        if not self.evolution_stats:
            return {}

        generations = [s['generation'] for s in self.evolution_stats]
        best_fits = [s['best'] for s in self.evolution_stats]
        mean_fits = [s['mean'] for s in self.evolution_stats]

        return {
            'generation': generations,
            'best_fitness': best_fits,
            'mean_fitness': mean_fits
        }

    def save_results(self, output_dir: str = './ga_results'):
        """
        Sauvegarder les résultats de l'évolution

        Args:
            output_dir: Répertoire de sortie
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Sauvegarder stats
        stats_file = output_path / f"stats_{datetime.now().isoformat()}.json"
        with open(stats_file, 'w') as f:
            json.dump(self.evolution_stats, f, indent=2)

        # Sauvegarder meilleur individu
        best = self.get_best_individual()
        best_file = output_path / "best_individual.npy"
        np.save(best_file, best.chromosome.get_genes())

        if self.config.VERBOSE:
            print(f"Results saved to {output_path}")

    def __repr__(self):
        best_fit = self.get_best_individual().get_fitness() if self.best_individuals else -1
        return f"GA(gens={len(self.evolution_stats)}, best_fitness={best_fit:.3f})"



def simple_fitness_function(individual: Individual) -> float:
    """
    Fonction de fitness simple pour test
    
    Objectif: Maximiser la moyenne des gènes (tous les gènes = 1.0)
    """
    genes = individual.chromosome.genes
    
    # Fitness = moyenne des gènes
    return float(np.mean(genes))


def sphere_fitness_function(individual: Individual) -> float:
    """
    Fonction Sphere (problème classique d'optimisation)
    
    Objectif: Trouver tous les gènes = 0.5 (optimum global à 0.5)
    """
    genes = individual.chromosome.genes
    
    # Distance à l'optimum (0.5, 0.5, ...)
    distance = np.sqrt(np.sum((genes - 0.5) ** 2))
    
    # Fitness = inverse de la distance
    return 1.0 / (1.0 + distance)


def main():
    """Démonstration du GA"""
    random.seed(datetime.now().timestamp())
    np.random.seed(int(datetime.now().timestamp()))

    print("=" * 60)
    print("EDPac Genetic Algorithm Demo")
    print("=" * 60)
#
#     #Configuration
#     config = GAConfig(
#         population_config=PopulationConfig(
#             POPULATION_SIZE=5,
#             ELITE_SIZE=1,
#             NB_GENERATIONS=1
#         ),
#         selection_config=SelectionConfig(
#             SELECTION_MODE=SelectionMode.TOURNAMENT,
#             TOURNAMENT_SIZE=2
#         ),
#         crossover_config=CrossoverConfig(
#             CROSSOVER_RATE=0.8
#         ),
#         mutation_config=MutationConfig(
#             MUTATION_RATE=0.02,
#         ),
#         VERBOSE=True
#     )
    # Configuration
    config = GAConfig(
        population_config=PopulationConfig(
            POPULATION_SIZE=100,
            ELITE_SIZE=10,
            NB_GENERATIONS=50
        ),
        selection_config=SelectionConfig(
            SELECTION_MODE=SelectionMode.TOURNAMENT,
            TOURNAMENT_SIZE=10
        ),
        crossover_config=CrossoverConfig(
            CROSSOVER_RATE=0.8
        ),
        mutation_config=MutationConfig(
            MUTATION_RATE=0.02,
        ),
        VERBOSE=True
    )
    print("\nConfiguration:")
    print(f"  Population size: {config.population_config.POPULATION_SIZE}")
    print(f"  Generations: {config.population_config.NB_GENERATIONS}")
    print(f"  Mutation rate: {config.mutation_config.MUTATION_RATE}")
    print(f"  Crossover rate: {config.crossover_config.CROSSOVER_RATE}")
    
    # Créer GA
    print("\n" + "=" * 60)
    print("Test 1: Simple Fitness (Maximize Gene Average)")
    print("=" * 60)
    
    ga1 = GeneticAlgorithm(config, simple_fitness_function)
    best1 = ga1.run()
    
    print(f"\nBest fitness: {best1.get_fitness():.4f}")
    print(f"Best genes (first 10): {best1.chromosome.genes[:10]}")
    
    # Visualiser convergence
    curve = ga1.get_convergence_curve()
    print("\nConvergence (every 10 generations):")
    for i in range(0, len(curve['generation']), 5):
        gen = curve['generation'][i]
        best = curve['best_fitness'][i]
        mean = curve['mean_fitness'][i]
        print(f"  Gen {gen:3d}: best={best:.4f}, mean={mean:.4f}")
    
    # Test 2: Sphere function
    print("\n" + "=" * 60)
    print("Test 2: Sphere Function (Find Optimum at 0.5)")
    print("=" * 60)

    ga2 = GeneticAlgorithm(config, sphere_fitness_function)
    best2 = ga2.run()

    print(f"\nBest fitness: {best2.get_fitness():.4f}")
    print(f"Best genes (first 10): {best2.chromosome.genes[:10]}")
    print(f"Average gene value: {np.mean(best2.chromosome.genes):.4f}")
    print(f"Distance to optimum (0.5): {np.sqrt(np.sum((best2.chromosome.genes - 0.5)**2)):.4f}")

    # Sauvegarder résultats
    print("\n" + "=" * 60)
    print("Saving Results")
    print("=" * 60)
    ga1.save_results('./ga_results_demo')
    print("Results saved to ./ga_results_demo")

    print("\nDemo completed!")


if __name__ == "__main__":
    main()
