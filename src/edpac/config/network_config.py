"""
NetworkConfig.py - Remplace DefineEDNetwork.h

Configuration du réseau neuronal
"""

from dataclasses import dataclass
from enum import Enum

from .constants import NB_VISIO_INPUTS, NB_MOTOR_PATTERNS

class ProjectionNature(Enum):
    """Type de projection (synapses)"""
    EXCITATORY = "excit"
    INHIBITORY = "inhib"

class AssemblyNature(Enum):
    """Type d'assemblée"""
    INPUT = "input"
    OUTPUT = "output"
    HIDDEN = "hidden"

@dataclass
class NetworkConfig:
    """Configuration du réseau"""
    # Projection mode
    TOPOLOGICAL_PROJECTION: bool = True
    
    # Input/Output assemblies
    NB_INPUT_ASSEMBLIES = NB_VISIO_INPUTS # + NB_AUDIO_INPUTS
    NB_OUTPUT_ASSEMBLIES = NB_MOTOR_PATTERNS  # Number of motor patterns

    # Network topology
    SQRT_NB_ASSEMBLIES = 1
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


@dataclass
class NetworkVisualizerConfig:
    # for visio config
    GAP_INPUT_ASSEMBLY = 5 # gap in visu between assemblies
    GAP_HIDDEN_ASSEMBLY = 5
    GAP_OUTPUT_ASSEMBLY = 5

