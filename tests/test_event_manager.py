"""
test_event_manager.py

Tests unitaires pour EventManager
"""

import pytest
import sys
sys.path.insert(0, '../src')

from edpac.ed_network.event_manager import (
    EventManager, 
    PSPEvent, 
    SpikeEvent
)
from edpac.physiology.spiking_neuron import SpikingNeuron
from edpac.physiology.dynamic_synapse import DynamicSynapse
from edpac.config.physiology_config import NeuronConfig, SynapseConfig
from edpac.config.network_config import EventManagerConfig


class TestPSPEvent:
    """Tests pour PSPEvent"""
    
    def test_psp_event_creation(self):
        """Créer un événement PSP"""
        synapse = None  # Sera créé si nécessaire
        event = PSPEvent(time=10, synapse=synapse, weight=0.5)
        
        assert event.time == 10
        assert event.weight == 0.5
        assert event.synapse is None
    
    def test_psp_event_ordering(self):
        """Les événements sont ordonnés par temps"""
        event1 = PSPEvent(time=10, synapse=None, weight=0.5)
        event2 = PSPEvent(time=20, synapse=None, weight=0.5)
        
        assert event1 < event2


class TestSpikeEvent:
    """Tests pour SpikeEvent"""
    
    def test_spike_event_creation(self):
        """Créer un événement spike"""
        neuron = SpikingNeuron()
        event = SpikeEvent(time=15, neuron=neuron)
        
        assert event.time == 15
        assert event.neuron == neuron
    
    def test_spike_event_ordering(self):
        """Les spikes sont ordonnés par temps"""
        neuron = SpikingNeuron()
        event1 = SpikeEvent(time=10, neuron=neuron)
        event2 = SpikeEvent(time=20, neuron=neuron)
        
        assert event1 < event2


class TestEventManager:
    """Tests pour EventManager"""
    
    def test_event_manager_creation(self):
        """Créer un EventManager"""
        config = EventManagerConfig()
        manager = EventManager(config)
        
        assert manager.current_time == 0
        assert manager.is_empty == True
        assert manager.spike_count == 0
        assert manager.psp_count == 0
    
    def test_reset(self):
        """Réinitialiser le gestionnaire"""
        manager = EventManager()
        
        # Ajouter des événements (fictifs)
        neuron = SpikingNeuron()
        manager.schedule_spike(10, neuron)
        
        assert not manager.is_empty
        assert manager.spike_count == 1
        
        # Réinitialiser
        manager.reset()
        
        assert manager.current_time == 0
        assert manager.is_empty == True
        assert manager.spike_count == 0
    
    def test_schedule_spike(self):
        """Programmer un spike"""
        manager = EventManager()
        neuron = SpikingNeuron()
        
        manager.schedule_spike(10, neuron)
        
        assert not manager.is_empty
        assert manager.spike_count == 1
        assert manager.get_queue_size() == 1
    
    def test_schedule_spike_in_past_raises(self):
        """Ne pas permettre d'événement dans le passé"""
        manager = EventManager()
        neuron = SpikingNeuron()
        
        # Avancer le temps
        manager.current_time = 20
        
        # Essayer d'ajouter un spike dans le passé
        with pytest.raises(ValueError):
            manager.schedule_spike(10, neuron)
    
    def test_schedule_psp(self):
        """Programmer un PSP"""
        manager = EventManager()
        synapse_config = SynapseConfig(DELAY=5)
        
        neuron1 = SpikingNeuron()
        neuron2 = SpikingNeuron()
        synapse = DynamicSynapse(neuron1, neuron2, synapse_config)
        
        manager.schedule_psp(synapse, spike_time=10)
        
        assert not manager.is_empty
        assert manager.psp_count == 1
    
    def test_run_one_step_empty_queue(self):
        """run_one_step sur queue vide retourne None"""
        manager = EventManager()
        
        result = manager.run_one_step()
        
        assert result is None
        assert manager.is_empty
    
    def test_run_one_step_with_event(self):
        """run_one_step traite un événement"""
        manager = EventManager()
        neuron = SpikingNeuron()
        
        manager.schedule_spike(10, neuron)
        events = manager.run_one_step()
        
        assert events is not None
        assert len(events) == 1
        assert events[0].time == 10
        assert manager.current_time == 10
    
    def test_run_one_step_multiple_events_same_time(self):
        """run_one_step traite tous les événements au même temps"""
        manager = EventManager()
        neuron1 = SpikingNeuron()
        neuron2 = SpikingNeuron()
        
        # Programmer deux spikes au même temps
        manager.schedule_spike(10, neuron1)
        manager.schedule_spike(10, neuron2)
        
        events = manager.run_one_step()
        
        assert len(events) == 2
        assert all(e.time == 10 for e in events)
    
    def test_run_until(self):
        """run_until exécute jusqu'à un temps donné"""
        manager = EventManager()
        neuron = SpikingNeuron()
        
        # Programmer des spikes à différents temps
        manager.schedule_spike(10, neuron)
        manager.schedule_spike(20, neuron)
        manager.schedule_spike(30, neuron)
        
        event_count = manager.run_until(25)
        
        assert manager.current_time == 20
        assert event_count == 2  # Spikes à 10 et 20
    
    def test_get_time(self):
        """get_time retourne le temps courant"""
        manager = EventManager()
        
        assert manager.get_time() == 0
        
        manager.current_time = 42
        assert manager.get_time() == 42
    
    def test_get_empty(self):
        """get_empty retourne l'état de la queue"""
        manager = EventManager()
        assert manager.get_empty() == True
        
        neuron = SpikingNeuron()
        manager.schedule_spike(10, neuron)
        assert manager.get_empty() == False
    
    def test_get_queue_size(self):
        """get_queue_size retourne la taille"""
        manager = EventManager()
        neuron = SpikingNeuron()
        
        assert manager.get_queue_size() == 0
        
        manager.schedule_spike(10, neuron)
        manager.schedule_spike(20, neuron)
        
        assert manager.get_queue_size() == 2
    
    def test_inject_input(self):
        """Injecter un input externe"""
        manager = EventManager()
        neuron = SpikingNeuron()
        
        manager.inject_input(neuron, 15, weight=0.1)
        
        assert manager.psp_count == 1
        assert not manager.is_empty


class TestEventManagerIntegration:
    """Tests d'intégration pour EventManager"""
    
    def test_simple_spike_propagation(self):
        """Tester la propagation simple d'un spike"""
        manager = EventManager()
        
        # Créer deux neurones connectés
        neuron1 = SpikingNeuron()
        neuron2 = SpikingNeuron()
        
        config = SynapseConfig(DELAY=5, WEIGHT=0.2)
        synapse = DynamicSynapse(neuron1, neuron2, config)
        
        # Injecter un input dans neuron1
        manager.inject_input(neuron1, time=10, weight=0.05)
        
        # Exécuter jusqu'à t=20
        manager.run_until(20)
        
        # Vérifier que neuron1 a reçu l'input
        assert neuron1.last_time_of_psp_impact >= 10
    
    def test_multiple_neurons_network(self):
        """Tester un petit réseau de neurones"""
        manager = EventManager()
        
        # Créer 3 neurones
        neurons = [SpikingNeuron() for _ in range(3)]
        
        # Connecter en chaîne: N0 -> N1 -> N2
        config = SynapseConfig(DELAY=3, WEIGHT=0.15)
        syn01 = DynamicSynapse(neurons[0], neurons[1], config)
        syn12 = DynamicSynapse(neurons[1], neurons[2], config)
        
        # Injecter un signal dans N0
        manager.inject_input(neurons[0], time=10, weight=0.08)
        
        # Exécuter la simulation
        manager.run_until(50)
        
        # Vérifier que le signal s'est propagé
        assert manager.get_psp_count() > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])