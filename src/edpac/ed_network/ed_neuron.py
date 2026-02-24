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
        super().__init__(config)
    
    def emit_spike(self, spike_time: int):
        """
        Émettre un spike et le programmer dans l'EventManager
        
        Args:
            spike_time: Temps du spike (ms)
        """
        self.last_time_of_firing = spike_time
        self.spike_times.append(spike_time)
        
        if len(self.incoming_links):
            for synapse in self.incoming_links:
                synapse.update_last_time_of_post_spike(spike_time)

        # Programmer le spike dans le EventManager
        manager = EDSynapse.get_event_manager()
        manager.schedule_spike(spike_time, self)
    
    def compute_psp_impact(self, time_of_impact: int, weight_of_impact: float):
        """Traiter l'impact d'un PSP"""
        #self.compute_spike_emission(time_of_impact, weight_of_impact)

        if self.compute_spike_emission(time_of_impact, weight_of_impact):
            print(f"***** Emitting spike at {time_of_impact}*****")
            self.emit_spike(time_of_impact)


    def __repr__(self):
        return f"EDNeuron({self.index}, V={self.membrane_potential:.4f})"
