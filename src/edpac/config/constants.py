"""
Constants.py - Remplace Define.h

Toutes les constantes globales du projet
"""

# Temps et potentiels
# Tous les temps sont en secondes
# Tous les potentiels sont en millivolts

# Pacman parameters (from DefineZoo.h concept)
PACMAN_NB_OUTPUTS = 4  # 4 directions

# Input/Output assemblies
NB_INPUT_ASSEMBLIES = PACMAN_NB_OUTPUTS

# Network topology
SQRT_NB_ASSEMBLIES = 5
NB_ASSEMBLIES = SQRT_NB_ASSEMBLIES * SQRT_NB_ASSEMBLIES

SQRT_NB_NEURONS = 10
NB_NEURONS_EACH_ASSEMBLY = SQRT_NB_NEURONS * SQRT_NB_NEURONS

NB_HIDDEN_NEURONS = NB_NEURONS_EACH_ASSEMBLY * NB_ASSEMBLIES

# Other parameters
NB_OUTPUT_ASSEMBLIES = 4  # Number of motor patterns
NB_VISIO_INPUTS = 4
NB_AUDIO_INPUTS = 1
NB_MOTOR_PATTERNS = 4