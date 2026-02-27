"""
EvoNetwork.py - Réseau neuronal évolutionnaire

Construit le réseau à partir d'un chromosome GA
"""

import random

import numpy as np
from typing import List, Dict, Optional, Tuple

from itertools import product


from ..ed_network.network import Network
from ..ed_network.assembly import Assembly
from ..ed_network.ed_neuron import EDNeuron  # ✅ UTILISER EDNeuron
from ..ed_network.ed_synapse import EDSynapse  # ✅ UTILISER EDSynapse
from ..ed_network.event_manager import EventManager

from ..config.network_config import NetworkConfig, AssemblyNature, ProjectionNature
from ..config.physiology_config import NeuronConfig, SynapseConfig

from ..config.constants import *

synapse_config=SynapseConfig()

class EDNetwork(Network):
    """
    Réseau construit par algorithme génétique

    Le chromosome code les connexions et les poids
    """

    def __init__(self,
                 config: NetworkConfig = None,
                 neuron_config: NeuronConfig = None):
        """
        Créer un réseau à partir d'un chromosome

        Args:
            chromosome: Chromosome GA
            config: Configuration réseau
            neuron_config: Configuration neurones
        """
        super().__init__(config, neuron_config)

        self._build_assemblies()

        # ✅ Créer et définir le EventManager pour toutes les synapses
        self.event_manager = EventManager()
        EDSynapse.set_event_manager(self.event_manager)

        # Statistiques
        self.total_spikes = 0
        self.total_simulation_time = 0

    def reset(self):
        """Réinitialiser le réseau"""

        super().reset()

        self.event_manager.reset()

    def inject_input_float(self, assembly_idx: int, time: int, pattern_float: np.ndarray):
        """
        Injecter un input dans une assemblée input

        Args:
            assembly_idx: Index de l'assemblée input
            time: Temps d'injection
            pattern_float: Pattern d'activation (valeurs entre 0 et 1)
        """
        if assembly_idx >= len(self.input_assemblies):
            raise IndexError(f"Input assembly {assembly_idx} not found")

        assembly = self.input_assemblies[assembly_idx]

        if len(pattern_float) != assembly.get_nb_neurons():
            raise ValueError(f"Pattern size {len(pattern_float)} != assembly size {assembly.get_nb_neurons()}")

        # Injecter stochastiquement selon le pattern
        for neuron_idx, activation in enumerate(pattern_float):
            neuron = assembly.get_neuron(neuron_idx)
            neuron.emit_spike(time + (1.0 - activation)*synapse_config.TEMPORAL_WAVE_LENGTH)

                #self.event_manager.inject_input(neuron, time, weight=activation)


    def inject_input(self, assembly_idx: int, time: int, pattern: np.ndarray):
        """
        Injecter un input dans une assemblée input

        Args:
            assembly_idx: Index de l'assemblée input
            time: Temps d'injection
            pattern: Pattern d'activation (valeurs entre 0 et 1)
        """
        if assembly_idx >= len(self.input_assemblies):
            raise IndexError(f"Input assembly {assembly_idx} not found")

        assembly = self.input_assemblies[assembly_idx]

        if len(pattern) != assembly.get_nb_neurons():
            raise ValueError(f"Pattern size {len(pattern)} != assembly size {assembly.get_nb_neurons()}")

        # Injecter stochastiquement selon le pattern
        for neuron_idx, activation in enumerate(pattern):
            if np.random.rand() < activation:
                neuron = assembly.get_neuron(neuron_idx)
                neuron.emit_spike(time)
                #self.event_manager.inject_input(neuron, time, weight=activation)

    def simulate(self, duration: int) -> Dict:
        """
        Simuler le réseau

        Args:
            duration: Durée de la simulation (ms)

        Returns:
            Statistiques de simulation
        """
        self.event_manager.reset()

        # Réinitialiser le réseau
        for assembly_list in [self.input_assemblies, self.hidden_assemblies, self.output_assemblies]:
            for assembly in assembly_list:
                assembly.reset()

        # Exécuter la simulation
        event_count = self.event_manager.run_until(duration)

        # Collecter les statistiques
        stats = {
            'duration': duration,
            'total_events': event_count,
            'spike_counts': {},
            'assembly_activities': {}
        }

        # Compter les spikes par assemblée
        for assembly_list in [self.input_assemblies, self.hidden_assemblies, self.output_assemblies]:
            for assembly in assembly_list:
                spike_count = sum(1 for n in assembly.neurons if n.last_time_of_firing > -1)
                stats['spike_counts'][assembly.id] = spike_count
                stats['assembly_activities'][assembly.id] = assembly.get_activity()

        self.total_simulation_time += duration

        return stats

    def get_output_pattern(self) -> np.ndarray:
        """
        Retourner le pattern de sortie

        Chaque valeur = nombre de spikes du neurone / max

        Returns:
            Pattern de sortie
        """
        if not self.output_assemblies:
            return np.array([])

        # Récupérer toutes les activités de sortie
        output_activities = []
        for assembly in self.output_assemblies:
            for neuron in assembly.neurons:
                spike_count = len(neuron.spike_times)
                output_activities.append(spike_count)

        if not output_activities:
            return np.zeros(len(self.output_assemblies))

        # Normaliser
        max_spikes = max(output_activities) if max(output_activities) > 0 else 1
        return np.array(output_activities) / max_spikes
