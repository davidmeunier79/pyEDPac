"""
NetworkBuilder.py - Constructeur pour créer des réseaux facilement
"""

import numpy as np
from ..ed_network.network import Network
from ..ed_network.assembly import Assembly
from ..config.network_config import NetworkConfig, AssemblyNature, ProjectionNature
from ..config.physiology_config import NeuronConfig, SynapseConfig

class NetworkBuilder:
    """Constructeur pour réseaux"""
    
    def __init__(self):
        """Initialiser le constructeur"""
        self.network = Network()
        self.assemblies_by_name = {}
    
    def add_input_assembly(self, name: str, nb_neurons: int) -> 'NetworkBuilder':
        """Ajouter une assemblée input"""
        assembly = Assembly(
            nb_neurons=nb_neurons,
            nature=AssemblyNature.INPUT,
            position=(0, len(self.network.input_assemblies))
        )
        self.network.add_assembly(assembly)
        self.assemblies_by_name[name] = assembly
        return self
    
    def add_hidden_assembly(self, name: str, nb_neurons: int, position: tuple = None) -> 'NetworkBuilder':
        """Ajouter une assemblée hidden"""
        if position is None:
            position = (1, len(self.network.hidden_assemblies))
        
        assembly = Assembly(
            nb_neurons=nb_neurons,
            nature=AssemblyNature.HIDDEN,
            position=position
        )
        self.network.add_assembly(assembly)
        self.assemblies_by_name[name] = assembly
        return self
    
    def add_output_assembly(self, name: str, nb_neurons: int) -> 'NetworkBuilder':
        """Ajouter une assemblée output"""
        assembly = Assembly(
            nb_neurons=nb_neurons,
            nature=AssemblyNature.OUTPUT,
            position=(2, len(self.network.output_assemblies))
        )
        self.network.add_assembly(assembly)
        self.assemblies_by_name[name] = assembly
        return self
    
    def connect(self, 
                from_name: str, 
                to_name: str,
                connection_ratio: float = 1.0,
                nature: ProjectionNature = ProjectionNature.EXCITATORY,
                weight: float = 0.5) -> 'NetworkBuilder':
        """Connecter deux assemblées"""
        
        if from_name not in self.assemblies_by_name:
            raise ValueError(f"Assembly {from_name} not found")
        if to_name not in self.assemblies_by_name:
            raise ValueError(f"Assembly {to_name} not found")
        
        pre_assembly = self.assemblies_by_name[from_name]
        post_assembly = self.assemblies_by_name[to_name]
        
        synapse_config = SynapseConfig(
            WEIGHT=weight,
            INITIAL_WEIGHT_MODE="fixed"
        )
        
        self.network.create_projection(
            pre_assembly,
            post_assembly,
            connection_ratio=connection_ratio,
            nature=nature,
            synapse_config=synapse_config
        )
        
        return self
    
    def build(self) -> Network:
        """Construire et retourner le réseau"""
        return self.network


# Exemple d'utilisation
def create_simple_pacman_network() -> Network:
    """Créer un réseau simple pour Pacman"""
    
    builder = NetworkBuilder()
    
    # Inputs: 4 directions + vision
    builder.add_input_assembly("vision", 20)
    builder.add_input_assembly("state", 4)
    
    # Hidden layers
    builder.add_hidden_assembly("hidden1", 50)
    builder.add_hidden_assembly("hidden2", 50)
    
    # Outputs: 4 directions (haut, bas, gauche, droite)
    builder.add_output_assembly("actions", 4)
    
    # Connexions
    (builder
     .connect("vision", "hidden1", connection_ratio=1.0, weight=0.3)
     .connect("state", "hidden1", connection_ratio=1.0, weight=0.5)
     .connect("hidden1", "hidden2", connection_ratio=0.8, weight=0.4)
     .connect("hidden2", "actions", connection_ratio=1.0, weight=0.6)
     .connect("hidden1", "actions", connection_ratio=0.5, weight=0.2))
    
    return builder.build()