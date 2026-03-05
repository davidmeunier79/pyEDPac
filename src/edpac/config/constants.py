"""
Constants.py - Remplace Define.h

Toutes les constantes globales du projet
"""

# Temps et potentiels
# Tous les temps sont en secondes
# Tous les potentiels sont en millivolts


DATA_PATH = "/home/INT/meunier.d/Tools/Packages/pyEdPac/data"
#DATA_PATH = "/envau/work/nit/users/meunier.d/Packages/pyEDPac/data"


# Pacman parameters (from DefineZoo.h concept)
NB_MOTOR_PATTERNS = 4

NB_VISIO_INPUTS = 5
#NB_AUDIO_INPUTS = 2

VISIO_COLUMN_DEPTH = 6

MINIMAL_TIME = 5
MOTOR_THRESHOLD = 0.5 # if half of the neuron of the output assembly spikes in MINIMAL TIME , trigger output)


# Input/Output assemblies
NB_INPUT_ASSEMBLIES = NB_VISIO_INPUTS # + NB_AUDIO_INPUTS
NB_OUTPUT_ASSEMBLIES = NB_MOTOR_PATTERNS  # Number of motor patterns

# Network topology
SQRT_NB_ASSEMBLIES = 5
NB_ASSEMBLIES = SQRT_NB_ASSEMBLIES * SQRT_NB_ASSEMBLIES

SQRT_NB_NEURONS = 5
NB_NEURONS_EACH_ASSEMBLY = SQRT_NB_NEURONS * SQRT_NB_NEURONS
NB_HIDDEN_NEURONS = NB_NEURONS_EACH_ASSEMBLY * NB_ASSEMBLIES

# Other parameters
MOTOR_SQRT_NB_NEURONS=5
VISIO_SQRT_NB_NEURONS=20

# for genes
NB_IN_ASSEMBLIES = NB_INPUT_ASSEMBLIES + NB_ASSEMBLIES
NB_OUT_ASSEMBLIES = NB_OUTPUT_ASSEMBLIES + NB_ASSEMBLIES

# for visio config
GAP_INPUT_ASSEMBLY = 5 # gap in visu between assemblies
GAP_HIDDEN_ASSEMBLY = 5
GAP_OUTPUT_ASSEMBLY = 5





#TODO ZooConfig?
INITIAL_LIFE_POINTS = 100

NB_LIFE_POINTS_PER_PACGUM = 2
NB_LIFE_POINTS_PER_PREY = 100
NB_LIFE_POINTS_PER_PREDATOR = 10

ZOO_NB_ROWS = 22
ZOO_NB_COLS = 40

ZOO_CELL_SIZE = VISIO_SQRT_NB_NEURONS

BLURRED_FACTOR = 0.2
