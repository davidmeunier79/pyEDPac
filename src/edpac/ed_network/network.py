"""
Network.py - Réseau neuronal complet

Gère les assemblées et les connexions
"""

import numpy as np
from typing import List, Dict, Optional, Tuple

from ..ed_network.assembly import Assembly
from ..config.physiology_config import NeuronConfig, SynapseConfig
from ..config.network_config import NetworkConfig, ProjectionNature, AssemblyNature
from ..config.constants import *

class Network:
    """
    Réseau neuronal complet
    
    Contient:
    - Assemblées de neurones
    - Connexions (synapses)
    - Event manager pour simulation
    """
    
    def __init__(self, config: NetworkConfig = None, neuron_config: NeuronConfig = None):
        """
        Créer un réseau
        
        Args:
            config: Configuration du réseau
        """
        self.config = config or NetworkConfig()
        
        self.neuron_config = neuron_config or NeuronConfig()

        # Assemblées par type
        self.input_assemblies: List[Assembly] = []
        self.hidden_assemblies: List[Assembly] = []
        self.output_assemblies: List[Assembly] = []

        self._build_assemblies()

    def _build_assemblies(self):

        # Créer les assemblées
        # Standard: input, hidden, output

        # Input assemblies
        for i in range(NB_INPUT_ASSEMBLIES):
            assembly = Assembly(
                nb_neurons=VISIO_SQRT_NB_NEURONS*VISIO_SQRT_NB_NEURONS,
                nature=AssemblyNature.INPUT,
                position=(0, i),
                neuron_config=self.neuron_config
            )
            self.add_assembly(assembly)

        # Hidden assemblies (5x5 grid = 25 assemblies)
        for x in range(SQRT_NB_ASSEMBLIES):
            for y in range(SQRT_NB_ASSEMBLIES):
                assembly = Assembly(
                    nb_neurons=NB_NEURONS_EACH_ASSEMBLY,
                    nature=AssemblyNature.HIDDEN,
                    position=(x+1, y),
                    neuron_config=self.neuron_config
                )
                self.add_assembly(assembly)

        # Output assemblies (4 pour actions Pacman)
        for i in range(NB_OUTPUT_ASSEMBLIES):
            assembly = Assembly(
                nb_neurons=MOTOR_SQRT_NB_NEURONS*MOTOR_SQRT_NB_NEURONS,
                nature=AssemblyNature.OUTPUT,
                position=(SQRT_NB_ASSEMBLIES+2, i),
                neuron_config=self.neuron_config
            )
            self.add_assembly(assembly)

    def add_assembly(self, assembly: Assembly) -> int:
        """
        Ajouter une assemblée
        
        Args:
            assembly: Assemblée à ajouter
            
        Returns:
            ID de l'assemblée
        """
        if assembly.nature == AssemblyNature.INPUT:
            self.input_assemblies.append(assembly)
        elif assembly.nature == AssemblyNature.OUTPUT:
            self.output_assemblies.append(assembly)
        else:
            self.hidden_assemblies.append(assembly)
        
        return assembly.id
    
    def reset(self):
        """Réinitialiser le réseau"""

        for assembly_list in [self.input_assemblies, self.hidden_assemblies, self.output_assemblies]:
            for assembly in assembly_list:
                assembly.reset()

    def get_nb_neurons(self) -> int:
        """Retourner le nombre total de neurones"""
        count = 0

        for assembly_list in [self.input_assemblies, self.hidden_assemblies, self.output_assemblies]:
            for assembly in assembly_list:
                count += assembly.get_nb_neurons()

        return count
    
    def __repr__(self):
        return (f"Network(neurons={self.get_nb_neurons()}, "
                f"assemblies={len(self.input_assemblies)}, {len(self.hidden_assemblies)} , {len(self.output_assemblies)})")
