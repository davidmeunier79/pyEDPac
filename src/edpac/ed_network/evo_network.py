"""
EvoNetwork.py - Réseau neuronal évolutionnaire

Construit le réseau à partir d'un chromosome GA
"""

import numpy as np
from typing import List
from ..ed_network.ed_network import EDNetwork

from ..topology.node import Node
from ..topology.link import Link

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
                 neuron_config: NeuronConfig = None,
                 synapse_config: SynapseConfig = None):
        """
        Créer un réseau à partir d'un chromosome
        
        Args:
            chromosome: Chromosome GA
            config: Configuration réseau
            neuron_config: Configuration neurones
        """
        super().__init__(config, neuron_config)

        Node._node_count = 0
        Link._link_count = 0

        self.synapse_config = synapse_config or SynapseConfig
        self.chromosome = chromosome

        # Construire le réseau
        # Décoder le chromosome et créer les projections
        self._create_projections_from_chromosome()

        self._reorganise_synapses()

    def get_neuron_from_id(self, neuron_id):

        all_assemblies = self.input_assemblies + self.hidden_assemblies + self.output_assemblies
        print(len(all_assemblies))

        for assembly in all_assemblies:
            for neuron in assembly.neurons:

                if neuron.id == neuron_id:
                    return neuron

    def _create_projections_from_chromosome(self):
        """Créer les projections en décodant le chromosome"""
        
        if self.chromosome.config.VARIABLE_LENGTH_CHROMOSOME:

            # Pour chaque projection codée
            projection_complete = False

            pre_id= -1
            proj_nature = -1
            post_id=-1

            nb_in_assemblies = self.config.NB_INPUT_ASSEMBLIES
            nb_out_assemblies = self.config.NB_OUTPUT_ASSEMBLIES


            for gene_id, gene in enumerate(self.chromosome.get_genes()):

                # print("Gene: ", gene_id)

                if gene_id %3 == 0:
                    projection_complete = False

                    pre_id=int(gene*nb_in_assemblies)
                    proj_nature = -1
                    post_id = -1

                elif gene_id %3 == 1:
                    proj_nature = (gene < 0.5 )

                elif gene_id %3 == 2:
                    post_id = int(gene*nb_out_assemblies)

                if pre_id == -1 or proj_nature == -1 or post_id == -1:
                    projection_complete = False
                    continue

                projection_complete = True
                #
                # print("*** projection_complete ** ")
                # print("pre_id ", pre_id )
                # print("proj_nature ", proj_nature )
                # print("post_id ", post_id)

                if len(self.projections) % self.chromosome.config.NB_PROJECTIONS_PER_HIDDEN_ASSEMBLY == 0:

                    if (nb_in_assemblies+1) < self.config.NB_IN_ASSEMBLIES :
                        nb_in_assemblies=nb_in_assemblies+1

                    else:
                        print(f"Error , too many nb_in_assemblies = {nb_in_assemblies}")
                        print(f"(Already {len(self.projections)} projections stored)")

                    if (nb_out_assemblies+1) < self.config.NB_OUT_ASSEMBLIES :
                        nb_out_assemblies=nb_out_assemblies+1

                    else:
                        print(f"Error , too many nb_out_assemblies = {nb_out_assemblies}")
                        print(f"(Already {len(self.projections)} projections stored)")

                # Mapper les indices aux assemblées
                if pre_id < self.config.NB_INPUT_ASSEMBLIES:
                    pre_assembly = self.input_assemblies[pre_id]

                else:
                    pre_id = pre_id - self.config.NB_INPUT_ASSEMBLIES
                    pre_assembly = self.hidden_assemblies[pre_id]

                if post_id < self.config.NB_OUTPUT_ASSEMBLIES:
                    post_assembly = self.output_assemblies[post_id]

                else:
                    post_id = post_id - self.config.NB_OUTPUT_ASSEMBLIES
                    post_assembly = self.hidden_assemblies[post_id]

                # Déterminer le type (excitatory par défaut)
                if proj_nature:
                    nature = ProjectionNature.EXCITATORY

                else:
                    nature = ProjectionNature.INHIBITORY

                projection = self.create_projection(
                    pre_assembly,
                    post_assembly,
                    connection_ratio=1.0,  # Utiliser weight pour ratio
                    nature=nature,
                    synapse_config=self.synapse_config
                )

                if projection is not None:
                    self.projections.append(projection)
        else:

            # Pour chaque projection codée
            projection_complete = False

            pre_id= -1
            proj_nature = -1
            post_id=-1

            for gene_id, gene in enumerate(self.chromosome.get_genes()):

                if gene_id %3 == 0:
                    projection_complete = False

                    pre_id=int(gene*self.config.NB_IN_ASSEMBLIES)
                    proj_nature = -1
                    post_id = -1

                elif gene_id %3 == 1:
                    proj_nature = (gene < 0.5 )

                elif gene_id %3 == 2:
                    post_id = int(gene*self.config.NB_OUT_ASSEMBLIES)

                if pre_id == -1 or proj_nature == -1 or post_id == -1:
                    projection_complete = False
                    continue

                projection_complete = True

                # Mapper les indices aux assemblées
                if pre_id < self.config.NB_INPUT_ASSEMBLIES:
                    pre_assembly = self.input_assemblies[pre_id]

                else:
                    pre_id = pre_id - self.config.NB_INPUT_ASSEMBLIES
                    pre_assembly = self.hidden_assemblies[pre_id]

                if post_id < self.config.NB_OUTPUT_ASSEMBLIES:
                    post_assembly = self.output_assemblies[post_id]

                else:
                    post_id = post_id - self.config.NB_OUTPUT_ASSEMBLIES
                    post_assembly = self.hidden_assemblies[post_id]

                # Déterminer le type (excitatory par défaut)
                if proj_nature:
                    nature = ProjectionNature.EXCITATORY

                else:
                    nature = ProjectionNature.INHIBITORY

                projection = self.create_projection(
                    pre_assembly,
                    post_assembly,
                    connection_ratio=1.0,  # Utiliser weight pour ratio
                    nature=nature,
                    synapse_config=self.synapse_config
                )

                if projection is not None:
                    self.projections.append(projection)

    def _reorganise_synapses(self):
        """
        with INHIBITORY synapses first in the list
        """
        for assembly in self.hidden_assemblies:
            for neuron in assembly.get_neurons():
                neuron._reorganise_synapses()
