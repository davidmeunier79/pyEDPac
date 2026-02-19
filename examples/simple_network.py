"""
Simple Network Example

Démonstration de création et simulation d'un petit réseau neuronal
"""

import sys
sys.path.insert(0, '../src')

from edpac import (
    Neuron, 
    SpikingNeuron,
    DynamicSynapse,
    SynapseConfig,
    NeuronConfig
)

def main():
    # Configuration
    neuron_config = NeuronConfig()
    synapse_config = SynapseConfig()
    
    # Créer 3 neurones
    neurons = [SpikingNeuron(neuron_config) for _ in range(3)]
    print(f"Created {len(neurons)} neurons")
    
    # Connecter les neurones
    synapse_config.WEIGHT = 0.1  # Poids fort
    synapses = []
    
    # N0 -> N1
    syn1 = DynamicSynapse(neurons[0], neurons[1], synapse_config)
    synapses.append(syn1)
    print(f"Created synapse: {syn1}")
    
    # N1 -> N2
    syn2 = DynamicSynapse(neurons[1], neurons[2], synapse_config)
    synapses.append(syn2)
    print(f"Created synapse: {syn2}")
    
    # Simuler quelques impulsions
    print("\n--- Simulation ---")
    
    # Input au neurone 0 à t=10ms
    neurons[0].compute_psp_impact(10, 0.1)
    print(f"t=10ms: Neuron 0 spike: {neurons[0].last_time_of_firing > -1}")
    
    # À t=20ms (avec délai), neurone 1 devrait recevoir PSP
    # (À implémenter complètement avec EventManager)
    
    print("\nNetwork structure:")
    for neuron in neurons:
        print(f"  {neuron}: {len(neuron.synapses_in)} inputs, {len(neuron.synapses_out)} outputs")

if __name__ == "__main__":
    main()