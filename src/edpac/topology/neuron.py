"""
Neuron.py - Équivalent à Neuron.h (classe de base pour neurones)
"""

from .node import Node

class Neuron(Node):
    """Classe de base pour les neurones"""
    
    def __init__(self):
        """Initialiser un neurone"""
        super().__init__()
        #self.synapses_in = []    # Synapses entrantes
        #self.synapses_out = []   # Synapses sortantes
#
#     def add_synapse_in(self, synapse):
#         """Ajouter une synapse entrante"""
#         self.synapses_in.append(synapse)
#
#     def add_synapse_out(self, synapse):
#         """Ajouter une synapse sortante"""
#         self.synapses_out.append(synapse)
#
    def compute_psp_impact(self, time_of_impact: int, weight_of_impact: float):
        """
        Traiter l'impact d'un PSP (Post-Synaptic Potential)
        
        Cette méthode est virtuelle et sera overridée par les sous-classes
        """
        raise NotImplementedError("Subclasses must implement compute_psp_impact")
    
    def _reorganise_synapses(self):

        self.outgoing_links.sort(key=lambda s: s.get_weight(), reverse=True)


    def __repr__(self):
        return f"Neuron({self.index})"
