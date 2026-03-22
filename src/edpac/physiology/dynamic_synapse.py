"""
DynamicSynapse.py - Équivalent à DynamicSynapse.h

Synapse avec plasticité et apprentissage (STDP)
"""

import numpy as np
from ..topology.synapse import Synapse
from ..config.physiology_config import SynapseConfig

class DynamicSynapse(Synapse):
    """Synapse avec plasticité dépendante du timing (STDP)"""
    
    def __init__(self, pre_neuron=None, post_neuron=None, config: SynapseConfig = None):
        """Initialiser une synapse dynamique"""
        super().__init__(pre_neuron, post_neuron, config)
        
        # Pour l'apprentissage STDP
        self.last_time_of_pre_spike = -1
        self.last_time_of_post_spike = -1
        
    def update_last_time_of_pre_spike(self, new_time: int):
        """Mettre à jour le temps du dernier spike pré-synaptique"""
        #self.last_time_of_pre_spike = new_time + self.delay
        self.last_time_of_pre_spike = new_time

    def update_last_time_of_post_spike(self, new_time: int):
        """Mettre à jour le temps du dernier spike post-synaptique"""
        self.last_time_of_post_spike = new_time

        if self.config.ONLINE_LEARNING:
            #print("ONLINE_LEARNING")
            self.compute_new_weight()
    
    def compute_new_weight(self):
        """
        Calculer le nouveau poids selon STDP

        Implémentation virtuelle - à overrider par sous-classes
        """
        raise NotImplementedError("Subclasses must implement compute_new_weight")

    def __repr__(self):
        return f"DynamicSynapse(w={self.last_time_of_pre_spike}, d={self.last_time_of_post_spike})"
