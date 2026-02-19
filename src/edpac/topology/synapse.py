"""
Synapse.py - Équivalent à Synapse.h (classe de base pour synapses)
"""

from .link import Link

class Synapse(Link):
    """Classe de base pour les synapses"""
    
    def __init__(self, pre_neuron=None, post_neuron=None):
        """
        Initialiser une synapse entre deux neurones
        
        Args:
            pre_neuron: Neurone pré-synaptique (source)
            post_neuron: Neurone post-synaptique (cible)
        """
        super().__init__(pre_neuron, post_neuron)
        
        # Enregistrer auprès des neurones
        if pre_neuron is not None:
            pre_neuron.add_synapse_out(self)
        if post_neuron is not None:
            post_neuron.add_synapse_in(self)
    
    def compute_psp_emission(self, time_of_emission: int):
        """
        Calculer l'émission d'un PSP
        
        Cette méthode est virtuelle et sera overridée par les sous-classes
        """
        raise NotImplementedError("Subclasses must implement compute_psp_emission")
    
    def __repr__(self):
        return f"Synapse({self.index}: N{self.pre_node.index} -> N{self.post_node.index})"