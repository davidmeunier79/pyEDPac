"""
EvoNetwork.py - Réseau neuronal évolutionnaire

Construit le réseau à partir d'un chromosome GA
"""

import numpy as np
from typing import List, Dict, Optional, Tuple


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

    def reset(self):
        """Réinitialiser le réseau"""

        super().reset()

        self.event_manager.reset()

    def initialize_inputs(self, time = 0):
        """
        Injecter tous les inputs dans input_assemblies

        Args:
            sensory_patterns: NB_VISIO_INPUTS
        """


        spike_neuron_ids = []
        for i in range(NB_VISIO_INPUTS):

            input_pattern = np.ones(shape = (VISIO_SQRT_NB_NEURONS,VISIO_SQRT_NB_NEURONS))

            init_spikes = self.inject_input(assembly_idx = i,  time = time , pattern = input_pattern.reshape(-1,1))
            spike_neuron_ids.extend(init_spikes)

        return spike_neuron_ids

    def integrate_inputs(self, sensory_patterns):
        """
        Injecter tous les inputs dans input_assemblies

        Args:
            sensory_patterns: NB_VISIO_INPUTS
        """
        assert len(sensory_patterns) == len(self.input_assemblies), \
            f"Error {len(sensory_patterns)} != {len(self.input_assemblies)}"

        time = EDSynapse.event_manager.get_time()


        spike_neuron_ids = []
        for i, pattern in enumerate(sensory_patterns):
            if pattern is None:
                continue

            assert pattern.shape == (VISIO_SQRT_NB_NEURONS, VISIO_SQRT_NB_NEURONS)

            spike_neuron_ids.extend(self.inject_input(assembly_idx = i,  time = time , pattern = pattern.reshape(-1,1)))

        return spike_neuron_ids

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

        spike_neuron_ids = []

        # Injecter stochastiquement selon le pattern
        for i, activation in enumerate(pattern):
            if np.random.rand() < activation:
                neuron = assembly.neurons[i]
                #print("Input spike in neuron ", i)
                neuron.emit_spike(time)
                spike_neuron_ids.append(neuron.id)

        return spike_neuron_ids
    #
    # def inject_input_float(self, assembly_idx: int, time: int, pattern_float: np.ndarray):
    #     """
    #     Injecter un input dans une assemblée input
    #
    #     Args:
    #         assembly_idx: Index de l'assemblée input
    #         time: Temps d'injection
    #         pattern_float: Pattern d'activation (valeurs entre 0 et 1)
    #     """
    #     if assembly_idx >= len(self.input_assemblies):
    #         raise IndexError(f"Input assembly {assembly_idx} not found")
    #
    #     assembly = self.input_assemblies[assembly_idx]
    #
    #     if len(pattern_float) != assembly.get_nb_neurons():
    #         raise ValueError(f"Pattern size {len(pattern_float)} != assembly size {assembly.get_nb_neurons()}")
    #
    #     # Injecter stochastiquement selon le pattern
    #     for neuron_idx, activation in enumerate(pattern_float):
    #         neuron = assembly.get_neuron(neuron_idx)
    #         neuron.emit_spike(time + (1.0 - activation)*synapse_config.TEMPORAL_WAVE_LENGTH)
    #
    #             #self.event_manager.inject_input(neuron, time, weight=activation)


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

    def init_output_patterns(self):

        if not self.output_assemblies:
            return np.array([])

        # Récupérer toutes les activités de sortie
        for assembly in self.output_assemblies:
            for neuron in assembly.neurons:
                neuron.spike_times = []


    def get_output_patterns(self) -> np.ndarray:
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
            spike_count = []

            for neuron in assembly.neurons:
                spike_count.append(len(neuron.spike_times))

            output_activities.append(np.sum(np.array(spike_count))/len(assembly.neurons))

        if not output_activities:
            return np.zeros(len(self.output_assemblies))

        return np.array(output_activities)
