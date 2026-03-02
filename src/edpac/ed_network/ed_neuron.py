"""
EDNeuron.py - Neurone évolutionnaire

Neurone with EventManager coordination
"""

from ..physiology.spiking_neuron import SpikingNeuron
from ..config.physiology_config import NeuronConfig
from .ed_synapse import EDSynapse

class EDNeuron(SpikingNeuron):
    """
    Neurone évolutionnaire (Event-Driven)
    
    Coordonne avec EDSynapse via le class-level EventManager
    """
    
    def __init__(self, config: NeuronConfig = None):
        """
        Créer un neurone évolutionnaire
        
        Args:
            config: Configuration neuronale
        """
        self.config = config or NeuronConfig()
        super().__init__()
    
    def emit_spike(self, spike_time: int):
        """
        Émettre un spike et le programmer dans l'EventManager
        
        Args:
            spike_time: Temps du spike (ms)
        """

        for synapse in self.incoming_links:
            synapse.update_last_time_of_post_spike(spike_time)

        # Pour chaque synapse sortante, programmer le PSP arrivant
        for synapse in self.outgoing_links:
            EDSynapse.event_manager.schedule_psp(synapse, spike_time)

            # Mise à jour STDP pour synapses pré-synaptiques
            synapse.update_last_time_of_pre_spike(spike_time)

    def compute_psp_impact(self, time_of_impact: int, weight_of_impact: float):
        """Traiter l'impact d'un PSP"""
        #self.compute_spike_emission(time_of_impact, weight_of_impact)

        if self.test_spike_emission(time_of_impact, weight_of_impact):

            #print(f"***** Emitting spike at {time_of_impact}*****")

            self.emit_spike(time_of_impact)

            return True
        else:
            return False


    def __repr__(self):
        return f"EDNeuron({self.id}, V={self.membrane_potential:.4f})"
