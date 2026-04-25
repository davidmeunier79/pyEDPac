"""
Constants.py - Remplace Define.h

Toutes les constantes globales du projet
"""

# Temps et potentiels
# Tous les temps sont en secondes
# Tous les potentiels sont en millivolts


# Pacman parameters (from DefineZoo.h concept)

import sys
sys.path.insert(0, '../src')

from dataclasses import dataclass
from edpac.config.constants import VISIO_SQRT_NB_NEURONS


from edpac.config.base_config import BaseConfig

@dataclass
class UrsinaConfig(BaseConfig):

    URSINA_MOVE_SPEED: int = 25
    URSINA_ROT_SPEED: int = 300
    MAX_REF_FRAME_REFRESH: float = 1/30

@dataclass
class MultiPacmanConfig(BaseConfig):

    VISIO_COLUMN_DEPTH: int = 6
    BLURRED_FACTOR = 0.2

    #MOTOR_THRESHOLD = 0.5 # if half of the neuron of the output assembly spikes in MINIMAL TIME , trigger output)
    MOTOR_THRESHOLD = 0.01 # if any spike in output_assembly , trigger output)

    ## Pacman Life
    INITIAL_LIFE_POINTS: int = 10000

    #NB_LIFE_POINTS_PER_PREY: int = 100
    NB_LIFE_POINTS_PER_PREDATOR_CONTACT: int = 1
    NB_LIFE_POINTS_PER_PREY_BITE: int = 1

    # Special 2 populations prey and predators
    NB_LIFE_POINTS_PER_PACGUM_PREY: int = 500
    NB_LIFE_POINTS_PER_PACGUM_PREDATOR: int = 0

    MIN_LIFE_FOR_REPROD_PREY: int = 1000
    MIN_LIFE_FOR_REPROD_PREDATOR: int = 5000

    # random otherwise all bodies and heads are facing RIGHT
    RANDOM_INIT_DIRECTION: bool = True

@dataclass
class PacmanConfig(BaseConfig):

    VISIO_COLUMN_DEPTH: int = 6
    BLURRED_FACTOR: int = 0.2

    #MOTOR_THRESHOLD = 0.5 # if half of the neuron of the output assembly spikes in MINIMAL TIME , trigger output)
    MOTOR_THRESHOLD: float = 0.01 # if any spike in output_assembly , trigger output)

    ## Pacman Life
    INITIAL_LIFE_POINTS: int = 100

    NB_LIFE_POINTS_PER_PACGUM: int = 2
    NB_LIFE_POINTS_PER_PREY: int = 100
    NB_LIFE_POINTS_PER_PREDATOR: int = 10
#TODO
# Unused but could
#
# @dataclass
# class ZooConfig:
#     NB_LIFE_POINTS_PER_PACGUM: int = 2
#     NB_LIFE_POINTS_PER_PREY: int = 100
#     NB_LIFE_POINTS_PER_PREDATOR: int = 10
#
#     #REGROWTH_PACGUM_RATE = 0.001 # rate of renewal of pacgums # now in constants
