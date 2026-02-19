"""
test_physiology.py

Tests unitaires pour SpikingNeuron et DynamicSynapse
"""

import pytest
import sys
sys.path.insert(0, '../src')

from edpac.physiology.spiking_neuron import SpikingNeuron
from edpac.physiology.dynamic_synapse import DynamicSynapse
from edpac.config.physiology_config import NeuronConfig, SynapseConfig


class TestSpikingNeuron:
    """Tests pour SpikingNeuron"""
    
    def test_neuron_creation(self):
        """Créer un neurone"""
        config = NeuronConfig()
        neuron = SpikingNeuron(config)
        
        assert neuron.membrane_potential == config.RESTING_POTENTIAL
        assert neuron.threshold_potential == config.THRESHOLD_REF
        assert neuron.last_time_of_firing == -1
    
    def test_neuron_reset(self):
        """Réinitialiser un neurone"""
        neuron = SpikingNeuron()
        
        # Modifier l'état
        neuron.membrane_potential = 0.5
        neuron.last_time_of_firing = 10
        
        # Réinitialiser
        neuron.reset_neuron()
        
        config = neuron.config
        assert neuron.membrane_potential == config.RESTING_POTENTIAL
        assert neuron.last_time_of_firing == -1
    
    def test_neuron_init(self):
        """Initialiser un neurone"""
        neuron = SpikingNeuron()
        neuron.init_neuron()
        
        # Devrait réinitialiser
        assert neuron.last_time_of_firing == -1
    
    def test_update_membrane_potential_decay(self):
        """Tester la décroissance du potentiel"""
        neuron = SpikingNeuron()
        
        # Donner un potentiel initial
        neuron.membrane_potential = 0.1
        neuron.last_time_of_psp_impact = 0
        
        # Mettre à jour
        potential = neuron.update_membrane_potential(current_time=10)
        
        # Devrait avoir décru
        assert potential < 0.1
        assert potential > 0.0
    
    def test_update_membrane_potential_clamps_lower(self):
        """Potentiel clamped à la limite inférieure"""
        neuron = SpikingNeuron()
        neuron.membrane_potential = neuron.config.HYPER_POLARISATION_POTENTIAL - 0.1
        
        neuron.update_membrane_potential(10)
        
        assert neuron.membrane_potential >= neuron.config.HYPER_POLARISATION_POTENTIAL
    
    def test_update_threshold_no_refractory(self):
        """Seuil normal sans période réfractaire"""
        config = NeuronConfig(ABSOLUTE_REFRACTORY=0, RELATIVE_REFRACTORY=0)
        neuron = SpikingNeuron(config)
        
        threshold = neuron.update_threshold_potential(10)
        
        assert threshold == config.THRESHOLD_REF
    
    def test_update_threshold_absolute_refractory(self):
        """Seuil infini durant période réfractaire absolue"""
        config = NeuronConfig(ABSOLUTE_REFRACTORY=10)
        neuron = SpikingNeuron(config)
        
        neuron.last_time_of_firing = 5
        
        threshold = neuron.update_threshold_potential(current_time=10)
        
        # Toujours en période réfractaire (10-5 = 5 < 10)
        assert threshold == float('inf')
    
    def test_update_threshold_after_absolute_refractory(self):
        """Seuil normal après période réfractaire absolue"""
        config = NeuronConfig(ABSOLUTE_REFRACTORY=5)
        neuron = SpikingNeuron(config)
        
        neuron.last_time_of_firing = 0
        
        threshold = neuron.update_threshold_potential(current_time=10)
        
        # Après ARP (10 > 5)
        assert threshold == config.THRESHOLD_REF
    
    def test_compute_spike_emission_below_threshold(self):
        """Pas de spike en-dessous du seuil"""
        neuron = SpikingNeuron()
        
        spike = neuron.compute_spike_emission(time_of_impact=10, weight_of_impact=0.0001)
        
        assert spike is False
        assert neuron.last_time_of_firing == -1
    
    def test_compute_spike_emission_above_threshold(self):
        """Spike généré au-dessus du seuil"""
        config = NeuronConfig(THRESHOLD_REF=0.01)  # Seuil bas
        neuron = SpikingNeuron(config)
        
        spike = neuron.compute_spike_emission(time_of_impact=10, weight_of_impact=0.05)
        
        assert spike is True
        assert neuron.last_time_of_firing == 10
    
    def test_get_last_time_of_firing(self):
        """Retourner le temps du dernier spike"""
        neuron = SpikingNeuron()
        
        assert neuron.get_last_time_of_firing() == -1
        
        neuron.last_time_of_firing = 42
        assert neuron.get_last_time_of_firing() == 42


class TestDynamicSynapse:
    """Tests pour DynamicSynapse"""
    
    def test_dynamic_synapse_creation(self):
        """Créer une synapse dynamique"""
        neuron1 = SpikingNeuron()
        neuron2 = SpikingNeuron()
        config = SynapseConfig(WEIGHT=0.5, DELAY=10)
        
        synapse = DynamicSynapse(neuron1, neuron2, config)
        
        assert synapse.weight == 0.5
        assert synapse.delay == 10
        assert synapse.pre_node == neuron1
        assert synapse.post_node == neuron2
    
    def test_dynamic_synapse_weight_random(self):
        """Poids aléatoire"""
        config = SynapseConfig(INITIAL_WEIGHT_MODE="random", WEIGHT=0.5)
        
        neuron1 = SpikingNeuron()
        neuron2 = SpikingNeuron()
        
        synapse = DynamicSynapse(neuron1, neuron2, config)
        
        # Poids aléatoire devrait être entre ~0 et ~1
        assert 0.0 <= synapse.weight <= 1.5
    
    def test_dynamic_synapse_weight_fixed(self):
        """Poids fixé"""
        config = SynapseConfig(INITIAL_WEIGHT_MODE="fixed", WEIGHT=0.5)
        
        neuron1 = SpikingNeuron()
        neuron2 = SpikingNeuron()
        
        synapse = DynamicSynapse(neuron1, neuron2, config)
        
        assert synapse.weight == 0.5
    
    def test_get_weight(self):
        """Retourner le poids"""
        neuron1 = SpikingNeuron()
        neuron2 = SpikingNeuron()
        synapse = DynamicSynapse(neuron1, neuron2, SynapseConfig(WEIGHT=0.3))
        
        assert synapse.get_weight() == 0.3
    
    def test_get_delay(self):
        """Retourner le délai"""
        neuron1 = SpikingNeuron()
        neuron2 = SpikingNeuron()
        synapse = DynamicSynapse(neuron1, neuron2, SynapseConfig(DELAY=7))
        
        assert synapse.get_delay() == 7
    
    def test_update_spike_timings(self):
        """Mettre à jour les timings de spikes"""
        neuron1 = SpikingNeuron()
        neuron2 = SpikingNeuron()
        synapse = DynamicSynapse(neuron1, neuron2, SynapseConfig(ONLINE_LEARNING=True))
        
        synapse.update_last_time_of_pre_spike(10)
        assert synapse.last_time_of_pre_spike == 10
        
        synapse.update_last_time_of_post_spike(15)
        assert synapse.last_time_of_post_spike == 15


class TestPhysiologyIntegration:
    """Tests d'intégration pour neurones et synapses"""
    
    def test_neuron_receives_psp(self):
        """Neurone reçoit un PSP"""
        config = NeuronConfig(THRESHOLD_REF=0.01)
        neuron = SpikingNeuron(config)
        
        # Appliquer un fort PSP
        neuron.compute_psp_impact(time_of_impact=10, weight_of_impact=0.05)
        
        # Devrait avoir enregistré l'impact
        assert neuron.last_time_of_psp_impact == 10
    
    def test_two_neurons_connected(self):
        """Tester deux neurones connectés"""
        config1 = NeuronConfig(THRESHOLD_REF=0.01)
        config2 = NeuronConfig(THRESHOLD_REF=0.01)
        
        neuron1 = SpikingNeuron(config1)
        neuron2 = SpikingNeuron(config2)
        
        syn_config = SynapseConfig(WEIGHT=0.05, DELAY=5)
        synapse = DynamicSynapse(neuron1, neuron2, syn_config)
        
        # Neuron1 génère un spike
        spike1 = neuron1.compute_spike_emission(10, weight_of_impact=0.05)
        
        if spike1:
            # Neuron2 reçoit le PSP après délai
            neuron2.compute_psp_impact(10 + synapse.get_delay(), synapse.get_weight())


if __name__ == "__main__":
    pytest.main([__file__, "-v"])