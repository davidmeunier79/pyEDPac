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
        super().__init__(pre_neuron, post_neuron)
        
        self.config = config or SynapseConfig()
        
        # Propriétés dynamiques
        self.weight = self._initialize_weight()
        self.delay = self._initialize_delay()
        
        # Pour l'apprentissage STDP
        self.last_time_of_pre_spike = -1
        self.last_time_of_post_spike = -1
        
        self.delta_weight = 0.0
        self.real_delta_weight = 0.0
    
    def _initialize_weight(self) -> float:
        """Initialiser le poids"""
#         #TODO
#         if self.config.INITIAL_WEIGHT_MODE == "fixed":
#             return self.config.WEIGHT
#         elif self.config.INITIAL_WEIGHT_MODE == "random":
#             sign = np.random.choice([-1, 1])
#             return self.config.WEIGHT * (1.0 + sign * np.random.random())
#         else:
#
        return self.config.WEIGHT
    
    def _initialize_delay(self) -> int:
        """Initialiser le délai de transmission"""
#
#         #TODO
#         if self.config.TOPOLOGICAL_DELAY:
#             # À implémenter: calculer délai topologique
#             return self.config.DELAY
#         else:

        # Délai aléatoire
        return np.random.randint(1, self.config.DELAY + 1)
    
    def get_weight(self) -> float:
        """Retourner le poids"""
        return self.weight
    
    def get_delay(self) -> int:
        """Retourner le délai"""
        return self.delay
    
    def update_last_time_of_pre_spike(self, new_time: int):
        """Mettre à jour le temps du dernier spike pré-synaptique"""
        self.last_time_of_pre_spike = new_time + self.delay
        if self.config.ONLINE_LEARNING:
            self.compute_new_weight()
    
    def update_last_time_of_post_spike(self, new_time: int):
        """Mettre à jour le temps du dernier spike post-synaptique"""
        self.last_time_of_post_spike = new_time
        if self.config.ONLINE_LEARNING:
            self.compute_new_weight()
    
    def compute_new_weight(self):
        """
        Calculer le nouveau poids selon STDP
        
        Implémentation virtuelle - à overrider par sous-classes
        """
        raise NotImplementedError("Subclasses must implement compute_new_weight")
    
    def __repr__(self):
        return f"DynamicSynapse(w={self.weight:.3f}, d={self.delay})"
