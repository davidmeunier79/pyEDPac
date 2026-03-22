"""
GAConfig.py - Configuration pour Algorithme Génétique

Remplace DefineGA.h
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List

class SelectionMode(Enum):
    """Mode de sélection"""
    TOURNAMENT = "tournament"
    #ROULETTE_WHEEL = "roulette_wheel"
    RANK = "rank"

class MutationMode(Enum):
    """Type de mutation"""
    GAUSSIAN = "gaussian"
    UNIFORM = "uniform"
    BIASED = "biased"

@dataclass
class ChromosomeConfig:
    """Configuration du chromosome"""
    # Encodage par projections
    PROJECTION_ENCODING: bool = True # TODO Not used except for NB_GENES_EACH_PROJECTION, so far always the case

    if PROJECTION_ENCODING:
        NB_GENES_EACH_PROJECTION: int = 3          # (pre_assembly, post_assembly, weight)

    #VARIABLE_LENGTH_CHROMOSOME : bool = False
    VARIABLE_LENGTH_CHROMOSOME : bool = True

    # Nombre de gènes
    if VARIABLE_LENGTH_CHROMOSOME:
        NB_PROJECTIONS_PER_HIDDEN_ASSEMBLY = 4 # if VARIABLE_LENGTH_CHROMOSOME=False
        NB_GENES_EACH_CHROMOSOME=NB_PROJECTIONS_PER_HIDDEN_ASSEMBLY*NB_GENES_EACH_PROJECTION*50 # corresponds to initial value
    else:
        NB_PROJECTIONS_EACH_CHROMOSOME: int = 360  # Nombre de projections
        NB_GENES_EACH_CHROMOSOME: int = NB_PROJECTIONS_EACH_CHROMOSOME*NB_GENES_EACH_PROJECTION

@dataclass
class PopulationConfig:
    """Configuration de la population"""
    # # # # Taille population
    POPULATION_SIZE: int = 100
    ELITE_SIZE: int = 10         # Meilleurs individus conservés

    # Génération
    NB_GENERATIONS: int = 30


@dataclass
class PopulationConfigTest:
    """Configuration de la population"""


        # Taille population
    POPULATION_SIZE: int = 5
    ELITE_SIZE: int = 1        # Meilleurs individus conservés

    # Génération
    NB_GENERATIONS: int = 3



@dataclass
class SelectionConfig:
    """Configuration de sélection"""
    # Mode
    SELECTION_MODE: SelectionMode = SelectionMode.TOURNAMENT ##Autre choix, ROULETTE_WHEEL
    
    # Tournoi
    #TOURNAMENT_SIZE: int = 2       # Nombre d'individus dans tournoi
    #TOURNAMENT_SIZE: int = 3       # Nombre d'individus dans tournoi
    TOURNAMENT_SIZE: int = 10       # Nombre d'individus dans tournoi
    
    # Roulette
    ROULETTE_BIAS: float = 2.0     # Biais pour meilleurs individus


@dataclass
class SelectionConfigTest:
    """Configuration de sélection"""
    # Mode
    SELECTION_MODE: SelectionMode = SelectionMode.TOURNAMENT ##Autre choix, ROULETTE_WHEEL

    # Tournoi
    TOURNAMENT_SIZE: int = 2       # Nombre d'individus dans tournoi
    #TOURNAMENT_SIZE: int = 3       # Nombre d'individus dans tournoi
    #TOURNAMENT_SIZE: int = 10       # Nombre d'individus dans tournoi

    # Roulette
    #ROULETTE_BIAS: float = 2.0     # Biais pour meilleurs individus # TODO

@dataclass
class CrossoverConfig:
    """Configuration de crossover"""
    # Taux
    CROSSOVER_RATE: float = 0.8    # 80% des offspring viennent de crossover
    #CROSSOVER_POINTS: int = 1      # One-point crossover
    
@dataclass
class MutationConfig:
    """Configuration de mutation"""
    # Taux
    MUTATION_RATE: float = 0.01    # 1% de mutation par gène
