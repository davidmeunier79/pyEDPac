"""
Constants.py - Remplace Define.h

Toutes les constantes globales du projet
"""

# Temps et potentiels
# Tous les temps sont en secondes
# Tous les potentiels sont en millivolts

# Pacman parameters (from DefineZoo.h concept)
NB_MOTOR_PATTERNS = 4

NB_VISIO_INPUTS = 5
#NB_AUDIO_INPUTS = 2

VISIO_COLUMN_DEPTH = 6

# Input/Output assemblies
NB_INPUT_ASSEMBLIES = NB_VISIO_INPUTS # + NB_AUDIO_INPUTS
NB_OUTPUT_ASSEMBLIES = NB_MOTOR_PATTERNS  # Number of motor patterns

# Network topology
SQRT_NB_ASSEMBLIES = 10
NB_ASSEMBLIES = SQRT_NB_ASSEMBLIES * SQRT_NB_ASSEMBLIES

SQRT_NB_NEURONS = 10
NB_NEURONS_EACH_ASSEMBLY = SQRT_NB_NEURONS * SQRT_NB_NEURONS
NB_HIDDEN_NEURONS = NB_NEURONS_EACH_ASSEMBLY * NB_ASSEMBLIES

# Other parameters
MOTOR_SQRT_NB_NEURONS=10
VISIO_SQRT_NB_NEURONS=20

# for genes
NB_IN_ASSEMBLIES = NB_INPUT_ASSEMBLIES + NB_ASSEMBLIES
NB_OUT_ASSEMBLIES = NB_OUTPUT_ASSEMBLIES + NB_ASSEMBLIES

# for visio
GAP_INPUT_ASSEMBLY = 20 # gap in visu between assemblies
GAP_HIDDEN_ASSEMBLY = 5
GAP_OUTPUT_ASSEMBLY = 20
