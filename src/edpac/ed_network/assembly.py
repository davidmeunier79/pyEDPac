"""
Assembly.py - Assemblée de neurones

Une assemblée = groupe de neurones avec même comportement
"""

import numpy as np
from typing import List, Optional

from .ed_neuron import EDNeuron

from ..config.physiology_config import NeuronConfig, SynapseConfig
from ..config.network_config import ProjectionNature, AssemblyNature

class Assembly:
    """
    Assemblée de neurones
    
    Représente un groupe de neurones avec une position topologique
    """
    
    _assembly_count = 0
    
    def __init__(self, 
                 nb_neurons: int,
                 nature: AssemblyNature = AssemblyNature.HIDDEN,
                 position: tuple = (0, 0),
                 neuron_config: NeuronConfig = None):
        """
        Créer une assemblée
        
        Args:
            nb_neurons: Nombre de neurones
            nature: Type d'assemblée (INPUT, OUTPUT, HIDDEN)
            position: Position topologique (x, y)
            neuron_config: Configuration des neurones
        """
        self.id = Assembly._assembly_count
        Assembly._assembly_count += 1
        
        self.nature = nature
        self.position = position  # (x, y) pour délai topologique
        
        self.neuron_config = neuron_config or NeuronConfig()
        
        # Créer les neurones
        self.neurons: List[EDNeuron] = [
            EDNeuron(self.neuron_config)
            for _ in range(nb_neurons)
        ]
        
        self.neuron_ids: List[int] = [neuron.id for neuron in self.neurons]

        # Historique d'activité
        self.spike_history = []
    
    def get_neuron_ids(self) -> List[int]:

        return self.neuron_ids

    def get_neuron(self, idx: int) -> EDNeuron:
        """Retourner un neurone par index"""
        if not idx in self.neuron_ids:
            print(f"!!!! Error with {idx}, not availaible in assembly {self.id}, ids = {self.neuron_ids}")

        index = self.neuron_ids[idx]

        neuron = self.neurons[index]

        assert neuron.id == idx, f"Error with stored neuron id {neuron.id}, should be = {idx}"

        return neuron
    
    def get_neurons(self) -> List[EDNeuron]:
        """Retourner tous les neurones"""
        return self.neurons
    
    def get_nb_neurons(self) -> int:
        """Retourner le nombre de neurones"""
        return len(self.neurons)
#
#     def add_outgoing_synapse(self, synapse: EDSynapse):
#         """Enregistrer une synapse sortante"""
#         self.outgoing_synapses.append(synapse)
#
    def reset(self):
        """Réinitialiser tous les neurones"""
        for neuron in self.neurons:
            neuron.reset_neuron()
        self.spike_history = []
    
    def get_activity(self) -> float:
        """
        Retourner l'activité de l'assemblée
        
        = proportion de neurones ayant tiré récemment
        
        Returns:
            Activité entre 0 et 1
        """
        if not self.neurons:
            return 0.0
        
        spiked_count = sum(1 for n in self.neurons if n.last_time_of_firing > -1)
        return spiked_count / len(self.neurons)
    
    def get_distance_to(self, other: 'Assembly') -> float:
        """
        Calculer la distance topologique à une autre assemblée
        
        Utilisé pour le délai topologique
        
        Args:
            other: Autre assemblée
            
        Returns:
            Distance euclidienne
        """
        x1, y1 = self.position
        x2, y2 = other.position
        return np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    
    def __repr__(self):
        return f"Assembly(id={self.id}, neurons={len(self.neurons)}, nature={self.nature.value})"
    
    @staticmethod
    def reset_count():
        """Réinitialiser le compteur"""
        Assembly._assembly_count = 0

        EDNeuron.reset_count()
