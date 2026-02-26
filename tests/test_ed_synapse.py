"""
test_ed_synapse.py - Tests pour EDSynapse avec EventManager centralisé
"""

import pytest
import sys
sys.path.insert(0, '../src')

from edpac.ed_network.ed_synapse import EDSynapse
from edpac.ed_network.ed_neuron import EDNeuron
from edpac.ed_network.event_manager import EventManager
from edpac.config.physiology_config import SynapseConfig, NeuronConfig



class TestEDSynapse:
    """Tests pour EDSynapse"""
    
    def setup_method(self):
        """Setup avant chaque test"""
        # Créer un EventManager pour les tests
        self.event_manager = EventManager()
        EDSynapse.set_event_manager(self.event_manager)
    
    def teardown_method(self):
        """Cleanup après chaque test"""
        EDSynapse.event_manager = None

    def test_set_event_manager(self):
        """Tester le setting du EventManager"""
        manager = EventManager()
        EDSynapse.set_event_manager(manager)
        
        assert EDSynapse.event_manager is manager
        assert EDSynapse.get_event_manager() is manager
    
    def test_get_event_manager_not_set(self):
        """Erreur si EventManager non défini"""
        EDSynapse.event_manager = None
        
        with pytest.raises(RuntimeError):
            EDSynapse.get_event_manager()
    
    def test_ed_synapse_creation(self):
        """Créer une EDSynapse"""
        pre_neuron = EDNeuron()
        post_neuron = EDNeuron()
        
        synapse = EDSynapse(pre_neuron, post_neuron, SynapseConfig())
        
        assert synapse.pre_node is pre_neuron
        assert synapse.post_node is post_neuron
    
    def test_ed_synapse_shared_event_manager(self):
        """Les synapses partagent le même EventManager"""
        pre = EDNeuron()
        post1 = EDNeuron()
        post2 = EDNeuron()
        
        syn1 = EDSynapse(pre, post1)
        syn2 = EDSynapse(pre, post2)
        
        # Les deux utilisent le même manager
        assert syn1.get_event_manager() is syn2.get_event_manager()
        assert syn1.get_event_manager() is self.event_manager
    
    def test_compute_spike_impact(self):
        """Tester l'impact d'un spike"""
        pre = EDNeuron()
        post = EDNeuron()
        synapse = EDSynapse(pre, post)
        
        # Programmer un spike
        pre.emit_spike(spike_time=10)
        
        # Vérifier que le PSP a été programmé
        assert self.event_manager.spike_count != 0
    
    def test_multiple_synapses_centralized_events(self):
        """Tester plusieurs synapses avec EventManager centralisé"""
        pre1 = EDNeuron()
        pre2 = EDNeuron()
        post = EDNeuron()
        
        syn1 = EDSynapse(pre1, post)
        syn2 = EDSynapse(pre2, post)
        
        # Programmer deux spikes

        pre1.emit_spike(spike_time=10)
        pre2.emit_spike(spike_time=15)

        # Tous les PSPs devraient être dans le même manager
        assert self.event_manager.spike_count == 2
        assert self.event_manager.get_queue_size() == 2
    
    def test_reset_event_manager(self):
        """Tester le reset du EventManager"""
        pre = EDNeuron()
        post = EDNeuron()
        synapse = EDSynapse(pre, post)
        
        pre.emit_spike(spike_time = 10)
        assert self.event_manager.spike_count == 1
        
        # Reset
        EDSynapse.reset_event_manager()
        assert self.event_manager.spike_count == 0


class TestEDNeuron:
    """Tests pour EDNeuron"""
    
    def setup_method(self):
        """Setup avant chaque test"""
        self.event_manager = EventManager()
        EDSynapse.set_event_manager(self.event_manager)
    
    def teardown_method(self):
        """Cleanup"""
        EDSynapse.event_manager = None
    
    def test_ed_neuron_emit_spike(self):
        """Tester l'émission d'un spike"""
        neuron = EDNeuron()
        
        neuron.emit_spike(spike_time=20)
        
        # Vérifier que le spike a été programmé
        assert neuron.last_time_of_firing == 20
        assert 20 in neuron.spike_times
        assert self.event_manager.spike_count == 1
    
    def test_ed_neuron_multiple_spikes(self):
        """Tester plusieurs spikes du même neurone"""
        neuron = EDNeuron()
        
        neuron.emit_spike(10)
        neuron.emit_spike(20)
        neuron.emit_spike(30)
        
        assert self.event_manager.spike_count == 3
        assert len(neuron.spike_times) == 3


class TestCentralizedEventHandling:
    """Tests pour gestion événementielle centralisée"""
    
    def setup_method(self):
        """Setup"""
        self.event_manager = EventManager()
        EDSynapse.set_event_manager(self.event_manager)
    
    def teardown_method(self):
        """Cleanup"""
        EDSynapse.event_manager = None
    
    def test_network_wide_event_handling(self):
        """Tester la gestion d'événements au niveau réseau"""
        # Créer un petit réseau
        neurons = [EDNeuron() for _ in range(5)]
        synapses = [
            EDSynapse(neurons[0], neurons[1]),
            EDSynapse(neurons[1], neurons[2]),
            EDSynapse(neurons[2], neurons[3]),
        ]
        
        # Générer des spikes
        neurons[0].emit_spike(10)
        neurons[1].emit_spike(15)
        neurons[2].emit_spike(20)
        
        # Tous les événements dans le même manager
        assert self.event_manager.spike_count == 3
        

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
