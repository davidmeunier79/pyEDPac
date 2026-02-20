"""
EvoNetwork.py - Réseau neuronal évolutionnaire

Construit le réseau à partir d'un chromosome GA
"""

import numpy as np
from typing import List
from ..ed_network.network import Network
from ..ed_network.assembly import Assembly
from ..genetic_algorithm.individual import Individual
from ..genetic_algorithm.chromosome import Chromosome
from ..config.network_config import NetworkConfig, AssemblyNature, ProjectionNature
from ..config.physiology_config import NeuronConfig, SynapseConfig
from ..config.ga_config import ChromosomeConfig

class EvoNetwork(Network):
    """
    Réseau construit par algorithme génétique
    
    Le chromosome code les connexions et les poids
    """
    
    def __init__(self, 
                 chromosome: Chromosome,
                 config: NetworkConfig = None,
                 neuron_config: NeuronConfig = None):
        """
        Créer un réseau à partir d'un chromosome
        
        Args:
            chromosome: Chromosome GA
            config: Configuration réseau
            neuron_config: Configuration neurones
        """
        super().__init__(config)
        
        self.chromosome = chromosome
        self.neuron_config = neuron_config or NeuronConfig()
        
        # Construire le réseau à partir du chromosome
        self._build_from_chromosome()
    
    def _build_from_chromosome(self):
        """Construire le réseau à partir du chromosome"""
        
        # Créer les assemblées
        # Standard: input, hidden, output
        
        # Input assemblies (ex: 4 pour Pacman)
        nb_input = 4
        for i in range(nb_input):
            assembly = Assembly(
                nb_neurons=10,
                nature=AssemblyNature.INPUT,
                position=(0, i),
                neuron_config=self.neuron_config
            )
            self.add_assembly(assembly)
        
        # Hidden assemblies (5x5 grid = 25 assemblies)
        sqrt_nb = 5
        hidden_idx = 0
        for x in range(sqrt_nb):
            for y in range(sqrt_nb):
                assembly = Assembly(
                    nb_neurons=25,
                    nature=AssemblyNature.HIDDEN,
                    position=(x+1, y),
                    neuron_config=self.neuron_config
                )
                self.add_assembly(assembly)
                hidden_idx += 1
        
        # Output assemblies (4 pour actions Pacman)
        for i in range(4):
            assembly = Assembly(
                nb_neurons=10,
                nature=AssemblyNature.OUTPUT,
                position=(sqrt_nb+1, i),
                neuron_config=self.neuron_config
            )
            self.add_assembly(assembly)
        
        # Décoder le chromosome et créer les projections
        self._create_projections_from_chromosome()
    
    def _create_projections_from_chromosome(self):
        """Créer les projections en décodant le chromosome"""
        
        # Récupérer tous les gènes du chromosome
        all_assemblies = (
            self.input_assemblies + 
            self.hidden_assemblies + 
            self.output_assemblies
        )
        
        # Pour chaque projection codée
        for proj_idx in range(self.chromosome.config.NB_PROJECTIONS_EACH_CHROMOSOME):
            pre_idx, post_idx, weight = self.chromosome.get_projection(proj_idx)
            
            # Mapper les indices aux assemblées
            pre_idx = pre_idx % len(all_assemblies)
            post_idx = post_idx % len(all_assemblies)
            
            pre_assembly = all_assemblies[pre_idx]
            post_assembly = all_assemblies[post_idx]
            
            # Éviter les auto-connexions
            if pre_idx == post_idx:
                continue
            
            # Créer la synapse
            synapse_config = SynapseConfig(
                WEIGHT=weight,
                INITIAL_WEIGHT_MODE="fixed"
            )
            
            # Déterminer le type (excitatory par défaut)
            nature = ProjectionNature.EXCITATORY
            
            self.create_projection(
                pre_assembly,
                post_assembly,
                connection_ratio=weight,  # Utiliser weight pour ratio
                nature=nature,
                synapse_config=synapse_config
            )
    
    @staticmethod
    def from_individual(individual: Individual, 
                        config: NetworkConfig = None) -> 'EvoNetwork':
        """
        Créer un réseau à partir d'un individu GA
        
        Args:
            individual: Individu GA
            config: Configuration réseau
            
        Returns:
            Nouveau réseau
        """
        return EvoNetwork(individual.chromosome, config)