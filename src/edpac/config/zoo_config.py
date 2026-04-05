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

    #MOTOR_THRESHOLD = 0.5 # if half of the neuron of the output assembly spikes in MINIMAL TIME , trigger output)
    MOTOR_THRESHOLD = 0.01 # if any spike in output_assembly , trigger output)

    ## Pacman Life
    INITIAL_LIFE_POINTS = 1000

    #NB_LIFE_POINTS_PER_PREY = 100
    NB_LIFE_POINTS_PER_PREDATOR_CONTACT = 100
    NB_LIFE_POINTS_PER_PREY_BITE = 100

    # Special 2 populations prey and predators
    NB_LIFE_POINTS_PER_PACGUM_PREY = 50
    NB_LIFE_POINTS_PER_PACGUM_PREDATOR = 1

    MIN_LIFE_FOR_REPROD = 100
    #MIN_LIFE_FOR_REPROD = INITIAL_LIFE_POINTS // 2


    #NB_LIFE_POINTS_PER_BITE = 5

@dataclass
class PacmanConfig:

    VISIO_COLUMN_DEPTH = 6
    BLURRED_FACTOR = 0.2

    #MOTOR_THRESHOLD = 0.5 # if half of the neuron of the output assembly spikes in MINIMAL TIME , trigger output)
    MOTOR_THRESHOLD = 0.01 # if any spike in output_assembly , trigger output)

    ## Pacman Life
    INITIAL_LIFE_POINTS = 100

    NB_LIFE_POINTS_PER_PACGUM = 2
    NB_LIFE_POINTS_PER_PREY = 100
    NB_LIFE_POINTS_PER_PREDATOR = 10

    #REGROWTH_PACGUM_RATE = 0.001 # rate of renewal of pacgums # now in constants
@dataclass
class ZooVisualizerConfig:
    ZOO_NB_ROWS = 22
    ZOO_NB_COLS = 40

    ZOO_CELL_SIZE = VISIO_SQRT_NB_NEURONS

