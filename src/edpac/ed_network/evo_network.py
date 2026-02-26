"""
EvoNetwork.py - Réseau neuronal évolutionnaire

Construit le réseau à partir d'un chromosome GA
"""

import numpy as np
from typing import List
from ..ed_network.ed_network import EDNetwork

from ..genetic_algorithm.individual import Individual
from ..genetic_algorithm.chromosome import Chromosome
from ..config.network_config import NetworkConfig, AssemblyNature, ProjectionNature
from ..config.physiology_config import NeuronConfig, SynapseConfig
from ..config.ga_config import ChromosomeConfig

from ..config.constants import *


class EvoNetwork(EDNetwork):
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
        super().__init__(config, neuron_config)
        
        self.chromosome = chromosome

        # Construire le réseau
        # Décoder le chromosome et créer les projections
        self._create_projections_from_chromosome()

    def _create_projections_from_chromosome(self):
        """Créer les projections en décodant le chromosome"""
        
        # Pour chaque projection codée
        for proj_idx in range(self.chromosome.config.NB_PROJECTIONS_EACH_CHROMOSOME):
            #print("Projection: ", proj_idx)
            pre_idx, proj_nature, post_idx  = self.chromosome.get_projection(proj_idx)
            #print("Gene values: ", pre_idx, " ", proj_nature," ", post_idx)

            # Mapper les indices aux assemblées
            if pre_idx < NB_INPUT_ASSEMBLIES:
                pre_assembly = self.input_assemblies[pre_idx]

            else:
                pre_idx = pre_idx - NB_INPUT_ASSEMBLIES
                pre_assembly = self.hidden_assemblies[pre_idx]

            if post_idx < NB_OUTPUT_ASSEMBLIES:
                post_assembly = self.output_assemblies[post_idx]

            else:
                post_idx = post_idx - NB_OUTPUT_ASSEMBLIES
                post_assembly = self.hidden_assemblies[post_idx]

            # Déterminer le type (excitatory par défaut)
            if proj_nature==0:
                nature = ProjectionNature.EXCITATORY

            elif proj_nature==1:
                nature = ProjectionNature.INHIBITORY


            self.create_projection(
                pre_assembly,
                post_assembly,
                connection_ratio=1.0,  # Utiliser weight pour ratio
                nature=nature,
                synapse_config=SynapseConfig()
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
