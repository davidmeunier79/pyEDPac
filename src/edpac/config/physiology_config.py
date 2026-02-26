"""
PhysiologyConfig.py - Remplace DefinePhysiology.h

Configuration physiologique des neurones et synapses
"""

from dataclasses import dataclass
from typing import Optional

@dataclass
class SynapseConfig:
    """Configuration des synapses"""
    # Paramètres de délai
    DELAY: int = 10              # Délai max excitateur (ms)
    INHIBITORY_DELAY: int = 1   # Délai max inhibiteur (ms)
    
    # Poids initial
    WEIGHT: float = 0.5          # Poids moyen
    INITIAL_WEIGHT_MODE: str = "random"  # "fixed" ou "random"
    
    # Modes
    NO_AUTO_CONNEXIONS: bool = True  # Pas d'autosynapses
    TOPOLOGICAL_DELAY: bool = False   # Délai basé topologie
    
    # STDP (Spike-Timing-Dependent Plasticity)
    ONLINE_LEARNING: bool = False
    EXCIT_ALPHA: float = 0.01    # Coefficient apprentissage excitateur
    INHIB_ALPHA: float = 0.01    # Coefficient apprentissage inhibiteur
    EXCIT_MULTIPLICATIVE: bool = True
    INHIB_MULTIPLICATIVE: bool = True

    TEMPORAL_WAVE_LENGTH : int = 20 # integration of inputs in a wave

@dataclass
class NeuronConfig:
    """Configuration des neurones"""
    # Potentiel de repos
    RESTING_POTENTIAL: float = 0.0  # mV
    
    # Seuil
    NB_MEAN_PSPS_TO_SPIKE: int = 20  # Nombre de PSPs pour spike
    THRESHOLD_REF: float = 2.0     # Seuil de référence
    
    # Refractory periods
    ABSOLUTE_REFRACTORY: int = 5     # ms (si défini)
    RELATIVE_REFRACTORY: int = 5     # ms (si défini)
    BURSTY_MODE: bool = True          # Bursting neurons
    
    # Inhibition
    HYPER_POLARISATION_POTENTIAL: float = -20  # mV
    INHIBITION_RESET_MODE: bool = True

@dataclass  
class EventManagerConfig:
    """Configuration du gestionnaire d'événements"""
    DELAY_STEP: int = 5
    MAX_DELAY: float = 7.07  # 1.414 * SQRT_NB_ASSEMBLIES
    PSP_EVENT_PACKAGE_SIZE: int = 10000

# Instances par défaut
DEFAULT_SYNAPSE_CONFIG = SynapseConfig()
DEFAULT_NEURON_CONFIG = NeuronConfig()
DEFAULT_EVENT_MANAGER_CONFIG = EventManagerConfig()
