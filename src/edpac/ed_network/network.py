"""
Network.py - Réseau neuronal complet

Gère les assemblées et les connexions
"""

import random

import numpy as np
from typing import List, Dict, Optional, Tuple

from itertools import product

from ..ed_network.projection import Projection
from ..ed_network.assembly import Assembly
from ..ed_network.ed_synapse import EDSynapse
from ..config.physiology_config import NeuronConfig, SynapseConfig
from ..config.network_config import NetworkConfig, ProjectionNature, AssemblyNature
#from ..config.constants import *

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

        self.projections: List[Projection] = []

    def _build_assemblies(self):

        # Créer les assemblées
        # Standard: input, hidden, output

        # Input assemblies
        for i in range(self.config.NB_INPUT_ASSEMBLIES):
            assembly = Assembly(
                nb_neurons=self.config.VISIO_SQRT_NB_NEURONS*self.config.VISIO_SQRT_NB_NEURONS,
                nature=AssemblyNature.INPUT,
                position=(0, i),
                neuron_config=self.neuron_config
            )
            self.add_assembly(assembly)

        # Hidden assemblies (5x5 grid = 25 assemblies)
        for x in range(self.config.SQRT_NB_ASSEMBLIES):
            for y in range(self.config.SQRT_NB_ASSEMBLIES):
                assembly = Assembly(
                    nb_neurons=self.config.NB_NEURONS_EACH_ASSEMBLY,
                    nature=AssemblyNature.HIDDEN,
                    position=(x+1, y),
                    neuron_config=self.neuron_config
                )
                self.add_assembly(assembly)

        # Output assemblies (4 pour actions Pacman)
        for i in range(self.config.NB_OUTPUT_ASSEMBLIES):
            assembly = Assembly(
                nb_neurons=self.config.MOTOR_SQRT_NB_NEURONS*self.config.MOTOR_SQRT_NB_NEURONS,
                nature=AssemblyNature.OUTPUT,
                position=(self.config.SQRT_NB_ASSEMBLIES+2, i),
                neuron_config=self.neuron_config
            )
            self.add_assembly(assembly)

    def create_projection(self,
                         pre_assembly: Assembly,
                         post_assembly: Assembly,
                         connection_ratio: float = 1.0,
                         nature: ProjectionNature = ProjectionNature.EXCITATORY,
                         synapse_config: SynapseConfig = None) -> List[EDSynapse]:
        """
        Créer une projection (ensemble de synapses)

        Args:
            pre_assembly: Assemblée pré-synaptique
            post_assembly: Assemblée post-synaptique
            connection_ratio: Ratio de connexions (1.0 = all-to-all)
            nature: Type de projection (excitatory/inhibitory)
            synapse_config: Configuration des synapses

        Returns:
            Liste des synapses créées
        """
        if synapse_config is None:
            synapse_config = SynapseConfig()

        # Calculer le délai topologique
        #TODO
        # topological_delay = 0
        # if self.config.TOPOLOGICAL_PROJECTION:
        #     distance = pre_assembly.get_distance_to(post_assembly)
        #     topological_delay = max(0, int(distance * 5))  # 5ms par unité

        if synapse_config.NO_AUTO_CONNEXIONS:
            if pre_assembly==post_assembly:
                return None

        # Sélectionner les connexions
        nb_pre = pre_assembly.get_nb_neurons()
        nb_post = post_assembly.get_nb_neurons()

        pre_indices = pre_assembly.get_neuron_ids()
        post_indices = post_assembly.get_neuron_ids()

        # Créer les synapses
        for pre_idx, post_idx in product(pre_indices, post_indices):

            if random.random() > connection_ratio:
                continue


            pre_neuron = pre_assembly.get_neuron(pre_idx)
            post_neuron = post_assembly.get_neuron(post_idx)

            # Ajuster le poids selon le type
            if nature == ProjectionNature.INHIBITORY:
                # Poids inhibiteur généralement plus faible
                synapse_config.WEIGHT = -synapse_config.WEIGHT
                synapse_config.DELAY = synapse_config.INHIBITORY_DELAY

            synapse = EDSynapse(pre_neuron, post_neuron, synapse_config)
            #
            # # Ajouter délai topologique
            # if topological_delay > 0:
            #     synapse.delay += topological_delay

            #synapses_created.append(synapse)
            #pre_neuron.add_outgoing_link(synapse)
            #post_neuron.add_incoming_link(synapse)

            # Enregistrer dans les assemblées
            #pre_assembly.add_outgoing_synapse(synapse)

        return Projection(pre_assembly.id, post_assembly.id, nature)

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
