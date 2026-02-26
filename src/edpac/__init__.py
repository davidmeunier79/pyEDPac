"""
EDPac Python - Event-Driven Pacman

Package principal pour la simulation de réseaux de neurones impulsionnels
"""

__version__ = "2.0.0"

# Imports des classes principales
from .topology.node import Node
from .topology.link import Link
from .topology.neuron import Neuron
from .topology.synapse import Synapse

from .physiology.dynamic_synapse import DynamicSynapse
from .physiology.spiking_neuron import SpikingNeuron

from .ed_network.ed_synapse import EDSynapse
from .ed_network.ed_neuron import EDNeuron


from .config.constants import *
from .config.physiology_config import (
    SynapseConfig, 
    NeuronConfig,
    DEFAULT_SYNAPSE_CONFIG,
    DEFAULT_NEURON_CONFIG
)
from .config.network_config import NetworkConfig

__all__ = [
    'Node',
    'Link', 
    'Neuron',
    'Synapse',
    'DynamicSynapse',
    'SpikingNeuron',
    'SynapseConfig',
    'NeuronConfig',
    'NetworkConfig',
]
