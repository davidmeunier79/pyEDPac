"""
ga_training.py

Exemple d'utilisation du Genetic Algorithm
"""

import sys
sys.path.insert(0, '../src')
import random
from datetime import datetime

import numpy as np
from edpac.genetic_algorithm.ga import GeneticAlgorithm
from edpac.genetic_algorithm.individual import Individual
from edpac.config.ga_config import (
    GAConfig, PopulationConfig, MutationConfig,
    CrossoverConfig, SelectionConfig, SelectionMode
)


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
