"""
NetworkConfig.py - Remplace DefineEDNetwork.h

Configuration du réseau neuronal
"""

from dataclasses import dataclass
from enum import Enum

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
class EventManagerConfig:
    """Configuration du gestionnaire d'événements"""
    DELAY_STEP: int = 5
    MAX_DELAY: float = 7.07  # 1.414 * SQRT_NB_ASSEMBLIES
    PSP_EVENT_PACKAGE_SIZE: int = 10000

@dataclass
class NetworkConfig:
    """Configuration du réseau"""
    # Projection mode
    ALL_TO_ALL_PROJECTION: bool = True  # Tous vers tous (vs ratio fixe)
    TOPOLOGICAL_PROJECTION: bool = True
    
    # Input modes
    STOCHASTIC_INPUT: bool = True  # Vs temporal coding
    BLOCKING_MODE: bool = False
    
    # Trace/Debug
    TRACE_MODE: bool = False
    TEXT_TRACE_MODE: bool = False
    GNUPLOT_TRACE_MODE: bool = False
    TEST_MODE: bool = False
    
    # Graph display
    GRAPHICAL_DISPLAY_MODE: bool = False
    
    # Statistics
    ASSEMBLY_STAT_MODE: bool = True
    GLOBAL_STAT_MODE: bool = True
    GLOBAL_SYNAPSE_STAT_MODE: bool = True

DEFAULT_NETWORK_CONFIG = NetworkConfig()
