"""
Constants.py - Remplace Define.h

Toutes les constantes globales du projet
"""

# Temps et potentiels
# Tous les temps sont en secondes
# Tous les potentiels sont en millivolts


# Pacman parameters (from DefineZoo.h concept)

from dataclasses import dataclass
from .constants import VISIO_SQRT_NB_NEURONS


@dataclass
class MultiPacmanConfig:

    VISIO_COLUMN_DEPTH = 6
    BLURRED_FACTOR = 0.2

    MOTOR_THRESHOLD = 0.5 # if half of the neuron of the output assembly spikes in MINIMAL TIME , trigger output)

    ## Pacman Life
    INITIAL_LIFE_POINTS = 100

    NB_LIFE_POINTS_PER_PREY = 100
    NB_LIFE_POINTS_PER_PREDATOR = 10

    # Special 2 populations prey and predators
    NB_LIFE_POINTS_PER_PACGUM_PREY = 5
    NB_LIFE_POINTS_PER_PACGUM_PREDATOR = 1

    NB_LIFE_POINTS_PER_BITE = 5

@dataclass
class PacmanConfig:

    VISIO_COLUMN_DEPTH = 6
    BLURRED_FACTOR = 0.2

    MOTOR_THRESHOLD = 0.5 # if half of the neuron of the output assembly spikes in MINIMAL TIME , trigger output)

    ## Pacman Life
    INITIAL_LIFE_POINTS = 100

    NB_LIFE_POINTS_PER_PACGUM = 2
    NB_LIFE_POINTS_PER_PREY = 100
    NB_LIFE_POINTS_PER_PREDATOR = 10


@dataclass
class ZooVisualizerConfig:
    ZOO_NB_ROWS = 22
    ZOO_NB_COLS = 40

    ZOO_CELL_SIZE = VISIO_SQRT_NB_NEURONS

