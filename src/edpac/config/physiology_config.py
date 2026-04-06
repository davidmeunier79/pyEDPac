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
    INHIBITORY_DELAY: int = 5   # Délai max inhibiteur (ms)
    DELAY_MODE : str = "random" # fixed or randome

    # Poids initial
    WEIGHT: float = 0.5          # Poids moyen
    INITIAL_WEIGHT_MODE: str = "random"  # "fixed" ou "random"
    
    # Modes
    NO_AUTO_CONNEXIONS: bool = True  # Pas d'autosynapses
    #TOPOLOGICAL_DELAY: bool = False   # Délai basé topologie
    
    # STDP (Spike-Timing-Dependent Plasticity)
    ONLINE_LEARNING: bool = True
    #ONLINE_LEARNING: bool = False

    EXCIT_ALPHA: float = 0.5    # Coefficient apprentissage excitateur

    INHIB_TIME_WINDOW: int = 10

    INHIB_ALPHA: float = 0.5    # Coefficient apprentissage inhibiteur

    #TEMPORAL_WAVE_LENGTH : int = 20 # integration of inputs in a wave

@dataclass
class NeuronConfig:
    """Configuration des neurones"""
    # Potentiel de repos
    RESTING_POTENTIAL: float = 0.0  # mV

    # Seuil
    #NB_MEAN_PSPS_TO_SPIKE: int = 20  # Nombre de PSPs pour spike
    #THRESHOLD_REF: float = 100.0     # Seuil de référence
    THRESHOLD_REF: float = 20.0     # Seuil de référence


    # Refractory periods
    ABSOLUTE_REFRACTORY: int = 5     # ms (si défini)
    #RELATIVE_REFRACTORY: int = 10     # ms (si défini)

    MEMBRANE_TIME_CONSTANT = 10.0  # ms (tau)


    #BURSTY_MODE: bool = True          # Bursting neurons
    BURSTY_MODE: bool = False          # Bursting neurons
    if BURSTY_MODE:
        THRESHOLD_TIME_CONSTANT: int = 10     # ms (si défini)
    
    # Inhibition
    #HYPER_POLARISATION_POTENTIAL: float = -20  # mV
    #INHIBITION_RESET_MODE: bool = True

@dataclass
class EventManagerConfig:
    """Configuration du gestionnaire d'événements"""
    DELAY_STEP: int = 5
    PSP_EVENT_PACKAGE_SIZE: int = 10000

