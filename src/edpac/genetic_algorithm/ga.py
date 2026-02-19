"""
GA.py - Algorithme Génétique principal

Orchestrate l'évolution de la population
"""

import numpy as np
from typing import Callable, List, Dict, Optional
import json
from datetime import datetime
from pathlib import Path

from .population import Population
from .individual import Individual
from ..config.ga_config import GAConfig

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
            size=config.population_config.POPULATION_SIZE,
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
            # self.population.evaluate(self.eval_func)
            # print("After evaluation ", gen)

            # Évoluer une génération
            best = self.population.evolve_generation(
                self.eval_func,
                elite_size=self.config.population_config.ELITE_SIZE
            )
            
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
