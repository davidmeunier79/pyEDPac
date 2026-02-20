"""
Network.py - Réseau neuronal complet

Gère les assemblées et les connexions
"""

import numpy as np
from typing import List, Dict, Optional, Tuple
from ..ed_network.assembly import Assembly
from ..physiology.spiking_neuron import SpikingNeuron
from ..physiology.dynamic_synapse import DynamicSynapse
from ..ed_network.event_manager import EventManager
from ..config.physiology_config import NeuronConfig, SynapseConfig
from ..config.network_config import NetworkConfig, ProjectionNature, AssemblyNature
from ..config.ga_config import ChromosomeConfig

class Network:
    """
    Réseau neuronal complet
    
    Contient:
    - Assemblées de neurones
    - Connexions (synapses)
    - Event manager pour simulation
    """
    
    def __init__(self, config: NetworkConfig = None):
        """
        Créer un réseau
        
        Args:
            config: Configuration du réseau
        """
        self.config = config or NetworkConfig()
        
        # Assemblées par type
        self.input_assemblies: List[Assembly] = []
        self.hidden_assemblies: List[Assembly] = []
        self.output_assemblies: List[Assembly] = []
        
        # Toutes les synapses
        self.all_synapses: List[DynamicSynapse] = []
        
        # Event manager
        self.event_manager = EventManager()
        
        # Statistiques
        self.total_spikes = 0
        self.total_simulation_time = 0
        self.spike_count_per_assembly: Dict[int, int] = {}
    
    def add_assembly(self, assembly: Assembly) -> int:
        """
        Ajouter une assemblée
        
        Args:
            assembly: Assemblée à ajouter
            
        Returns:
            ID de l'assemblée
        """
        if assembly.nature == AssemblyNature.INPUT:
            self.input_assemblies.append(assembly)
        elif assembly.nature == AssemblyNature.OUTPUT:
            self.output_assemblies.append(assembly)
        else:
            self.hidden_assemblies.append(assembly)
        
        self.spike_count_per_assembly[assembly.id] = 0
        return assembly.id
    
    def create_projection(self,
                         pre_assembly: Assembly,
                         post_assembly: Assembly,
                         connection_ratio: float = 1.0,
                         nature: ProjectionNature = ProjectionNature.EXCITATORY,
                         synapse_config: SynapseConfig = None) -> List[DynamicSynapse]:
        """
        Créer une projection (ensemble de synapses)
        
        Args:
            pre_assembly: Assemblée pré-synaptique
            post_assembly: Assemblée post-synaptique
            connection_ratio: Ratio de connexions (1.0 = all-to-all)
            nature: Type de projection (excitatory/inhibitory)
            synapse_config: Configuration des synapses
            
        Returns:
            Liste des synapses créées
        """
        if synapse_config is None:
            synapse_config = SynapseConfig()
        
        # Calculer le délai topologique
        topological_delay = 0
        if self.config.TOPOLOGICAL_PROJECTION:
            distance = pre_assembly.get_distance_to(post_assembly)
            topological_delay = max(0, int(distance * 5))  # 5ms par unité
        
        synapses_created = []
        
        # Sélectionner les connexions
        nb_pre = pre_assembly.get_nb_neurons()
        nb_post = post_assembly.get_nb_neurons()
        
        if connection_ratio >= 1.0:
            # All-to-all
            pre_indices = range(nb_pre)
            post_indices = range(nb_post)
        else:
            # Random subset
            nb_connections = max(1, int(nb_pre * nb_post * connection_ratio))
            pre_indices = np.random.choice(nb_pre, size=nb_connections)
            post_indices = np.random.choice(nb_post, size=nb_connections)
        
        # Créer les synapses
        for pre_idx, post_idx in zip(pre_indices, post_indices):
            pre_neuron = pre_assembly.get_neuron(pre_idx)
            post_neuron = post_assembly.get_neuron(post_idx)
            
            # Ajuster le poids selon le type
            if nature == ProjectionNature.INHIBITORY:
                # Poids inhibiteur généralement plus faible
                syn_config = SynapseConfig(
                    WEIGHT=synapse_config.WEIGHT * 0.5,
                    DELAY=synapse_config.INHIBITORY_DELAY
                )
            else:
                syn_config = synapse_config
            
            synapse = DynamicSynapse(pre_neuron, post_neuron, syn_config)
            
            # Ajouter délai topologique
            if topological_delay > 0:
                synapse.delay += topological_delay
            
            synapses_created.append(synapse)
            self.all_synapses.append(synapse)
            
            # Enregistrer dans les assemblées
            pre_assembly.add_outgoing_synapse(synapse)
        
        return synapses_created
    
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
                self.event_manager.inject_input(neuron, time, weight=activation)
    
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
    
    def reset(self):
        """Réinitialiser le réseau"""
        for assembly_list in [self.input_assemblies, self.hidden_assemblies, self.output_assemblies]:
            for assembly in assembly_list:
                assembly.reset()
        self.event_manager.reset()
    
    def get_nb_neurons(self) -> int:
        """Retourner le nombre total de neurones"""
        count = 0
        for assembly_list in [self.input_assemblies, self.hidden_assemblies, self.output_assemblies]:
            for assembly in assembly_list:
                count += assembly.get_nb_neurons()
        return count
    
    def get_nb_synapses(self) -> int:
        """Retourner le nombre total de synapses"""
        return len(self.all_synapses)
    
    def __repr__(self):
        return (f"Network(neurons={self.get_nb_neurons()}, "
                f"synapses={self.get_nb_synapses()}, "
                f"assemblies={len(self.input_assemblies) + len(self.hidden_assemblies) + len(self.output_assemblies)})")