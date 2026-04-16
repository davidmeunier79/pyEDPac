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

        # Statistiques
        self.stats = {"nb_total_projections": 0,
                      "nb_inhib_projections": 0, "nb_excit_projections": 0,
                      "nb_input_projections": 0, "nb_output_projections": 0,
                      "nb_direct_projections": 0, "nb_internal_projections": 0}


        # Construire le réseau
        # Décoder le chromosome et créer les projections
        print('_create_projections_from_chromosome')
        self._create_projections_from_chromosome(1)

        print('_reorganise_synapses')
        self._reorganise_synapses()

    def _create_projections_from_chromosome(self, verbose = 0):
        """Créer les projections en décodant le chromosome"""
        
        if self.chromosome.chromo_config.VARIABLE_LENGTH_CHROMOSOME:

            if self.chromosome.chromo_config.RELATIVE_ENCODING:

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

                    if len(self.projections) % self.chromosome.chromo_config.NB_PROJECTIONS_PER_HIDDEN_ASSEMBLY == 0:

                        if (nb_in_assemblies+1) < self.config.NB_IN_ASSEMBLIES :
                            nb_in_assemblies=nb_in_assemblies+1

                        # else:
                        #     print(f"Error , too many nb_in_assemblies = {nb_in_assemblies}")
                        #     print(f"(Already {len(self.projections)} projections stored)")

                        if (nb_out_assemblies+1) < self.config.NB_OUT_ASSEMBLIES :
                            nb_out_assemblies=nb_out_assemblies+1

                        # else:
                        #     print(f"Error , too many nb_out_assemblies = {nb_out_assemblies}")
                        #     print(f"(Already {len(self.projections)} projections stored)")

                    direct = 0
                    hidden = 0
                    # Mapper les indices aux assemblées
                    if pre_id < self.config.NB_INPUT_ASSEMBLIES:
                        pre_assembly = self.input_assemblies[pre_id]

                        self.stats["nb_input_projections"] += 1

                        direct += 1
                    else:
                        pre_id = pre_id - self.config.NB_INPUT_ASSEMBLIES
                        pre_assembly = self.hidden_assemblies[pre_id]

                        hidden += 1

                    if post_id < self.config.NB_OUTPUT_ASSEMBLIES:
                        post_assembly = self.output_assemblies[post_id]

                        self.stats["nb_output_projections"] += 1
                        direct += 1
                    else:
                        post_id = post_id - self.config.NB_OUTPUT_ASSEMBLIES
                        post_assembly = self.hidden_assemblies[post_id]

                        hidden += 1

                    if direct == 2:
                        self.stats["nb_direct_projections"] += 1

                    if hidden == 2:
                        self.stats["nb_internal_projections"] += 1

                    # Déterminer le type (excitatory par défaut)
                    if proj_nature:
                        nature = ProjectionNature.EXCITATORY
                        self.stats["nb_excit_projections"] += 1

                    else:
                        nature = ProjectionNature.INHIBITORY
                        self.stats["nb_inhib_projections"] += 1

                    projection = self.create_projection(
                        pre_assembly,
                        post_assembly,
                        event_manager = self.event_manager,
                        connection_ratio=1.0,  # Utiliser weight pour ratio
                        nature=nature,
                        synapse_config=self.synapse_config
                    )

                    if projection is not None:
                        self.stats["nb_total_projections"] += 1

                        self.projections.append(projection)

            else:
                assert self.chromosome.get_nb_genes() % self.chromosome.chromo_config.NB_GENES_EACH_PROJECTION == 0, \
                    "Error, {self.chromosome.nb_genes=} should be a multiple of {self.chromosome.chromo_config.NB_GENES_EACH_PROJECTION}"

                if verbose > 0:
                    print("VARIABLE_LENGTH_CHROMOSOME and not RELATIVE_ENCODING")

                nb_projections = self.chromosome.get_nb_genes() // self.chromosome.chromo_config.NB_GENES_EACH_PROJECTION

                if verbose > 0:
                    print(f"{nb_projections=}")

                # Pour chaque projection codée
                for proj_id in range(nb_projections):

                    if verbose > 0:
                        print(f"Projection {proj_id}")

                    #print("Projection: ", proj_idx)
                    pre_id, proj_nature, post_id  = self.chromosome.get_projection(proj_id)

                    if verbose > 0:
                        print(f"Gene values: {pre_id} {proj_nature} {post_id}")

                    # building projection
                    direct = 0
                    hidden = 0
                    # Mapper les indices aux assemblées
                    if pre_id < self.config.NB_INPUT_ASSEMBLIES:
                        pre_assembly = self.input_assemblies[pre_id]

                        self.stats["nb_input_projections"] += 1
                        direct += 1

                    else:
                        pre_id = pre_id - self.config.NB_INPUT_ASSEMBLIES
                        pre_assembly = self.hidden_assemblies[pre_id]
                        hidden += 1

                    if post_id < self.config.NB_OUTPUT_ASSEMBLIES:
                        post_assembly = self.output_assemblies[post_id]

                        self.stats["nb_output_projections"] += 1
                        direct += 1
                    else:
                        post_id = post_id - self.config.NB_OUTPUT_ASSEMBLIES
                        post_assembly = self.hidden_assemblies[post_id]

                        hidden += 1

                    if direct == 2:
                        self.stats["nb_direct_projections"] += 1

                    if hidden == 2:
                        self.stats["nb_internal_projections"] += 1

                    # Déterminer le type (excitatory par défaut)
                    if proj_nature:
                        nature = ProjectionNature.EXCITATORY
                        self.stats["nb_excit_projections"] += 1

                    else:
                        nature = ProjectionNature.INHIBITORY
                        self.stats["nb_inhib_projections"] += 1

                    projection = self.create_projection(
                        pre_assembly,
                        post_assembly,
                        event_manager = self.event_manager,
                        connection_ratio=1.0,  # Utiliser weight pour ratio
                        nature=nature,
                        synapse_config=SynapseConfig()
                    )

                    if projection is not None:
                        self.projections.append(projection)


        else:

            if self.chromosome.chromo_config.RELATIVE_ENCODING:

                print("RELATIVE_ENCODING=True and VARIABLE_LENGTH_CHROMOSOME=False ")
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

                    # building projection
                    direct = 0
                    hidden = 0
                    # Mapper les indices aux assemblées
                    if pre_id < self.config.NB_INPUT_ASSEMBLIES:
                        pre_assembly = self.input_assemblies[pre_id]

                        self.stats["nb_input_projections"] += 1
                        direct += 1
                    else:
                        pre_id = pre_id - self.config.NB_INPUT_ASSEMBLIES
                        pre_assembly = self.hidden_assemblies[pre_id]

                        hidden += 1

                    if post_id < self.config.NB_OUTPUT_ASSEMBLIES:
                        post_assembly = self.output_assemblies[post_id]

                        self.stats["nb_output_projections"] += 1
                        direct += 1
                    else:
                        post_id = post_id - self.config.NB_OUTPUT_ASSEMBLIES
                        post_assembly = self.hidden_assemblies[post_id]

                        hidden += 1

                    if direct == 2:
                        self.stats["nb_direct_projections"] += 1

                    if hidden == 2:
                        self.stats["nb_internal_projections"] += 1

                    # Déterminer le type (excitatory par défaut)
                    if proj_nature:
                        nature = ProjectionNature.EXCITATORY
                        self.stats["nb_excit_projections"] += 1

                    else:
                        nature = ProjectionNature.INHIBITORY
                        self.stats["nb_inhib_projections"] += 1

                    projection = self.create_projection(
                        pre_assembly,
                        post_assembly,
                        connection_ratio=1.0,  # Utiliser weight pour ratio
                        nature=nature,
                        synapse_config=self.synapse_config
                    )

                    if projection is not None:
                        self.projections.append(projection)

                        self.stats["nb_total_projections"] += 1

            else:
                print("RELATIVE_ENCODING=False and VARIABLE_LENGTH_CHROMOSOME=False ")

                # Pour chaque projection codée
                for proj_id in range(self.chromosome.chromo_config.NB_PROJECTIONS_EACH_CHROMOSOME):
                    #print("Projection: ", proj_idx)
                    pre_id, proj_nature, post_id  = self.chromosome.get_projection(proj_id)
                    #print("Gene values: ", pre_id, " ", proj_nature," ", post_id)

                    # building projection
                    direct = 0
                    hidden = 0
                    # Mapper les indices aux assemblées
                    if pre_id < self.config.NB_INPUT_ASSEMBLIES:
                        pre_assembly = self.input_assemblies[pre_id]

                        self.stats["nb_input_projections"] += 1
                        direct += 1

                    else:
                        pre_id = pre_id - self.config.NB_INPUT_ASSEMBLIES
                        pre_assembly = self.hidden_assemblies[pre_id]
                        hidden += 1

                    if post_id < self.config.NB_OUTPUT_ASSEMBLIES:
                        post_assembly = self.output_assemblies[post_id]

                        self.stats["nb_output_projections"] += 1
                        direct += 1
                    else:
                        post_id = post_id - self.config.NB_OUTPUT_ASSEMBLIES
                        post_assembly = self.hidden_assemblies[post_id]

                        hidden += 1

                    if direct == 2:
                        self.stats["nb_direct_projections"] += 1

                    if hidden == 2:
                        self.stats["nb_internal_projections"] += 1

                    # Déterminer le type (excitatory par défaut)
                    if proj_nature:
                        nature = ProjectionNature.EXCITATORY
                        self.stats["nb_excit_projections"] += 1

                    else:
                        nature = ProjectionNature.INHIBITORY
                        self.stats["nb_inhib_projections"] += 1

                    projection = self.create_projection(
                        pre_assembly,
                        post_assembly,
                        event_manager = self.event_manager,
                        connection_ratio=1.0,  # Utiliser weight pour ratio
                        nature=nature,
                        synapse_config=SynapseConfig()
                    )

                    if projection is not None:
                        self.projections.append(projection)

    def _reorganise_synapses(self):
        """
        with INHIBITORY synapses first in the list
        """
        for assembly in self.input_assemblies:
            for neuron in assembly.get_neurons():
                neuron._reorganise_synapses()

        for assembly in self.hidden_assemblies:
            for neuron in assembly.get_neurons():
                neuron._reorganise_synapses()

    def save_stats(self, indiv_path):

        import json
        import os

        if indiv_path==0:
            indiv_path = os.path.abspath("")

        file_stats = os.path.join(indiv_path, "Stats_evonetwork.json")

        with open(file_stats, 'w+') as fp:
            json.dump(self.stats, fp, indent=4)
