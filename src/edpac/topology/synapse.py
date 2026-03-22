"""
Synapse.py - Équivalent à Synapse.h (classe de base pour synapses)
"""

import numpy as np
from ..config.physiology_config import SynapseConfig

from .link import Link

class Synapse(Link):
    """Classe de base pour les synapses"""
    
    def __init__(self, pre_neuron=None, post_neuron=None, config: SynapseConfig = None):
        """
        Initialiser une synapse entre deux neurones
        
        Args:
            pre_neuron: Neurone pré-synaptique (source)
            post_neuron: Neurone post-synaptique (cible)
        """
        self.config = config or SynapseConfig()

        super().__init__(pre_neuron, post_neuron)


        # Propriétés dynamiques
        self.weight = self._initialize_weight()
        self.delay = self._initialize_delay()


    def _initialize_weight(self) -> float:
        """Initialiser le poids"""
#         #TODO
        if self.config.INITIAL_WEIGHT_MODE == "fixed":
            return self.config.WEIGHT
        elif self.config.INITIAL_WEIGHT_MODE == "random":
            return self.config.WEIGHT * (2.0 * np.random.random())
        else:
            print(f"Error with {self.config.INITIAL_WEIGHT_MODE}")
            return 0.0

    def _initialize_delay(self) -> int:
        """Initialiser le délai de transmission"""

        # Délai aléatoire
        #TODO
        return self.config.DELAY
        #return np.random.randint(self.config.DELAY - 2, self.config.DELAY + 3)

    def get_weight(self) -> float:
        """Retourner le poids"""
        return self.weight

    def get_delay(self) -> int:
        """Retourner le délai"""
        return self.delay


    def compute_psp_emission(self, time_of_emission: int):
        """
        Calculer l'émission d'un PSP
        
        Cette méthode est virtuelle et sera overridée par les sous-classes
        """
        raise NotImplementedError("Subclasses must implement compute_psp_emission")
    
    def __repr__(self):
        return f"DynamicSynapse(w={self.weight:.3f}, d={self.delay})"
