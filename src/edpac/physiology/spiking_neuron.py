"""
SpikingNeuron.py - Équivalent à SpikingNeuron.h

Neurone avec génération de spikes (event-driven)
"""

import numpy as np
from ..topology.neuron import Neuron
from ..config.physiology_config import NeuronConfig
#from ..math_tools.neuron_math import NeuronMathTools

class SpikingNeuron(Neuron):
    """Neurone générant des spikes (potentiels d'action)"""
    
    def __init__(self, config: NeuronConfig = None):
        """Initialiser un neurone avec spikes"""
        super().__init__()
        
        self.config = config or NeuronConfig()

        # État du neurone
        self.membrane_potential = self.config.RESTING_POTENTIAL
        #self.threshold_potential = self.config.THRESHOLD_REF
        
        # Timing
        self.last_time_of_psp_impact = -1
        self.last_time_of_firing = -1
        
        # Historique (pour traçage/stats)
        self.spike_times = []
    
    def init_neuron(self):
        """Initialiser le neurone"""
        self.reset_neuron()
    
    def reset_neuron(self):
        """Réinitialiser l'état du neurone"""
        self.membrane_potential = self.config.RESTING_POTENTIAL
        #self.threshold_potential = self.config.THRESHOLD_REF
        self.last_time_of_psp_impact = -1
        self.last_time_of_firing = -1
        self.spike_times = []
    
    def update_membrane_potential(self, current_time: int) -> float:
        """
        Mettre à jour le potentiel de membrane
        
        Applique la décroissance exponentielle ou linéaire
        """
        if self.last_time_of_psp_impact == -1:
            self.last_time_of_psp_impact = current_time
        
        time_elapsed = current_time - self.last_time_of_psp_impact
        
        #print(time_elapsed)
        #print(self.membrane_potential)
        # Décroissance du potentiel (simplifié)
        decay_factor = np.exp(-time_elapsed / self.config.MEMBRANE_TIME_CONSTANT)  # Tau = 50ms
        self.membrane_potential *= decay_factor
        #print(self.membrane_potential)
#
#         # Limiter aux bornes
#         self.membrane_potential = max(
#             self.config.HYPER_POLARISATION_POTENTIAL,
#             self.membrane_potential)

        
        return self.membrane_potential
    
    def update_threshold_potential(self, current_time: int) -> float:
        """
        Mettre à jour le seuil du neurone
        
        (Peut inclure période réfractaire absolue/relative)
        """
        if self.last_time_of_firing != -1:

            time_since_last_spike = current_time - self.last_time_of_firing

            if time_since_last_spike < self.config.ABSOLUTE_REFRACTORY:
                self.threshold_potential = float('inf')  # Impossible de tirer

                return

        # Seuil revient à la normale
        self.threshold_potential = self.config.THRESHOLD_REF
    
    def test_spike_emission(self, time_of_impact: int, weight_of_impact: float) -> bool:
        """
        Calculer et retourner si le neurone génère un spike
        
        Args:
            time_of_impact: Temps de l'impact du PSP
            weight_of_impact: Amplitude du PSP
            
        Returns:
            True si spike généré, False sinon
        """
        # Mettre à jour les potentiels
        self.update_membrane_potential(time_of_impact)
        self.update_threshold_potential(time_of_impact)
        
        # Ajouter l'impact du PSP
        #print("membrane_potential before PSP:", self.membrane_potential," ", current_threshold )
        self.membrane_potential += weight_of_impact
        #print("membrane_potential after PSP:", self.membrane_potential, " ", current_threshold )

        self.last_time_of_psp_impact = time_of_impact
        
        # Vérifier si spike
        if self.membrane_potential >= self.threshold_potential:

            #print("***** Spike emission:", self.membrane_potential, " ", current_threshold , " ", self.spike_times)
            self.spike_times.append(time_of_impact)
            self.last_time_of_firing = time_of_impact
            
            # Appliquer inhibition (hyperpolarisation)
            self.membrane_potential = self.config.RESTING_POTENTIAL
#
#             #TODO
#             if self.config.INHIBITION_RESET_MODE:
#                 self.membrane_potential = self.config.HYPER_POLARISATION_POTENTIAL
#             else:
#                 self.membrane_potential = self.config.RESTING_POTENTIAL
#
            return True
        
        return False

    def compute_psp_impact(self, time_of_impact: int, weight_of_impact: float):
        """Traiter l'impact d'un PSP"""
        raise NotImplementedError("Subclasses must implement compute_psp_impact")

    def get_last_time_of_firing(self) -> int:
        """Retourner le temps du dernier spike"""
        return self.last_time_of_firing
    
    def __repr__(self):
        return f"SpikingNeuron({self.index}, V={self.membrane_potential:.4f})"
