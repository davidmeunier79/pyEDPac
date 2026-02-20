"""
network_demo.py - Démonstration du Network
"""

import sys
sys.path.insert(0, '../src')

import numpy as np
from edpac.ed_network.network_builder import create_simple_pacman_network

def main():
    """Démonstration"""
    
    print("=" * 60)
    print("EDPac Network Demo")
    print("=" * 60)
    
    # Créer le réseau
    print("\nCreating simple Pacman network...")
    network = create_simple_pacman_network()
    
    print(f"\nNetwork Stats:")
    print(f"  Total neurons: {network.get_nb_neurons()}")
    print(f"  Total synapses: {network.get_nb_synapses()}")
    print(f"  Input assemblies: {len(network.input_assemblies)}")
    print(f"  Hidden assemblies: {len(network.hidden_assemblies)}")
    print(f"  Output assemblies: {len(network.output_assemblies)}")
    
    # Injecter des inputs
    print("\nInjecting random inputs...")
    vision_pattern = np.random.rand(20)  # Vision aléatoire
    network.inject_input(0, time=10, pattern=vision_pattern)
    
    state_pattern = np.array([0.5, 0.0, 0.0, 0.0])  # État
    network.inject_input(1, time=10, pattern=state_pattern)
    
    # Simuler
    print("\nSimulating for 100ms...")
    stats = network.simulate(duration=100)
    
    print(f"\nSimulation Results:")
    print(f"  Duration: {stats['duration']}ms")
    print(f"  Total events: {stats['total_events']}")
    
    # Récupérer output
    output_pattern = network.get_output_pattern()
    print(f"\nOutput Pattern (actions):")
    for i, val in enumerate(output_pattern):
        direction = ['UP', 'DOWN', 'LEFT', 'RIGHT'][i % 4]
        print(f"  {direction}: {val:.3f}")
    
    print("\nDemo completed!")


if __name__ == "__main__":
    main()