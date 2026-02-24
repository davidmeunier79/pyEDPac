"""
EDSynapse.py - Synapse avec EventManager au niveau classe

Synapse évolutionnaire avec gestion événementielle centralisée
"""

import numpy as np
from typing import Optional
from ..physiology.dynamic_synapse import DynamicSynapse
from ..config.physiology_config import SynapseConfig

class EDSynapse(DynamicSynapse):
    """
    Synapse évolutionnaire (Event-Driven)
    
    Utilise un EventManager au niveau classe pour la gestion centralisée
    des événements PSP/spike
    """
    
    # ✅ Class-level attribute - partagé par toutes les instances
    event_manager = None
    
    @classmethod
    def set_event_manager(cls, manager):
        """
        Définir le gestionnaire d'événements pour toutes les synapses
        
        Args:
            manager: EventManager instance
        """
        cls.event_manager = manager
    
    @classmethod
    def get_event_manager(cls):
        """Récupérer le gestionnaire d'événements"""
        if cls.event_manager is None:
            raise RuntimeError("EDSynapse.event_manager not set. Call EDSynapse.set_event_manager() first.")
        return cls.event_manager
    
    @classmethod
    def reset_event_manager(cls):
        """Réinitialiser le gestionnaire (utility)"""
        if cls.event_manager is not None:
            cls.event_manager.reset()
    
    def __init__(self, pre_neuron, post_neuron, config: SynapseConfig = None):
        """
        Créer une synapse évolutionnaire
        
        Args:
            pre_neuron: Neurone pré-synaptique
            post_neuron: Neurone post-synaptique
            config: Configuration synaptique
        """
        super().__init__(pre_neuron, post_neuron, config)
        
        # Pas besoin de stocker event_manager au niveau instance!
        # On utilise la version classe

    def compute_psp_emission(self, time_of_emission: int):
        """
        Émettre le PSP au neurone post-synaptique
        
        Args:
            time_of_emission: Temps d'émission (ms)
        """
        if self.post_node is not None:
            # Appliquer l'impact du PSP
            if self.post_node.compute_psp_emission(time_of_emission, self.get_weight()):
                self.update_last_time_of_post_spike(time_of_emission)
    
    def compute_bpsike_impact(self, time_of_bpsike: int):
        """
        Traiter l'impact d'un backpropagated spike (pour STDP)
        
        Args:
            time_of_bpsike: Temps du spike rétropropagé (ms)
        """
        # Mise à jour STDP via rétropropagation
        if hasattr(self, 'update_last_time_of_post_spike'):
            self.update_last_time_of_post_spike(time_of_bpsike)
    
    def __repr__(self):
        return (f"EDSynapse(pre={self.pre_node.id}, post={self.post_node.id}, "
                f"w={self.weight:.3f}, d={self.delay})")
