"""
Chromosome.py - Représentation du chromosome (génome)

Un chromosome code pour les connexions du réseau (projections, poids)
"""
import os
import numpy as np
from typing import List, Tuple
from copy import deepcopy
from ..config.ga_config import ChromosomeConfig

#from ..config.constants import *
from ..config.network_config import NetworkConfig

network_config = NetworkConfig()

class Chromosome:
    """
    Chromosome = Génome = Suite de gènes
    
    Représente la topologie et les paramètres du réseau neuronal
    """
    
    def __init__(self, config: ChromosomeConfig = None, genes: np.ndarray = None):
        """
        Créer un chromosome
        
        Args:
            config: Configuration du chromosome
            genes: Tableau de gènes (si None, généré aléatoirement)
        """
        self.chromo_config = config or ChromosomeConfig()
        
        if genes is not None:
            self.genes = np.array(genes, dtype=np.float32)

        else:
            # Générer aléatoirement
            self.genes = self._initialize_random_genes()
        
        # Valider la taille
        if not self.chromo_config.VARIABLE_LENGTH_CHROMOSOME:
            assert len(self.genes) == self.chromo_config.NB_GENES_EACH_CHROMOSOME, \
                f"Chromosome size mismatch: {len(self.genes)} != {self.chromo_config.NB_GENES_EACH_CHROMOSOME}"
    
    def _initialize_random_genes(self) -> np.ndarray:
        """Générer des gènes aléatoires"""


        if self.chromo_config.VARIABLE_LENGTH_CHROMOSOME:
            if self.chromo_config.RELATIVE_ENCODING:
                nb_genes = np.random.uniform(size = 1)
                #print(f"{nb_genes=}")
                #print(f"{self.chromo_config.NB_GENES_EACH_CHROMOSOME=}")
                nb_genes  = int(nb_genes[0]*self.chromo_config.NB_GENES_EACH_CHROMOSOME*2)
                #print(f"{nb_genes=}")
                genes = np.random.rand(nb_genes)

            else:
                #TODO
                #print("_initialize_random_genes VARIABLE_LENGTH_CHROMOSOME and not RELATIVE_ENCODING not implemented yet")

                nb_projections = int(np.random.uniform(size = 1)[0]*self.chromo_config.NB_PROJECTIONS_EACH_CHROMOSOME*2)

                while nb_projections==0:
                    nb_projections = int(np.random.uniform(size = 1)[0]*self.chromo_config.NB_PROJECTIONS_EACH_CHROMOSOME*2)

                #print(f"After _initialize_random_genes, {nb_projections=}")

                list_genes = [
                    np.random.randint(low = 0,
                                      high = network_config.NB_IN_ASSEMBLIES,
                                      size = nb_projections),
                    np.random.randint(low =0 ,
                                      high = 2,
                                      size = nb_projections),

                    np.random.randint(low = 0,
                                      high = network_config.NB_OUT_ASSEMBLIES,
                                      size = nb_projections)
                    ]


                genes = np.concatenate(np.array(list_genes, dtype = int).T, axis = 0)

                assert len(genes) % self.chromo_config.NB_GENES_EACH_PROJECTION == 0, f"Error, {len(genes)=} should be a multiple of {self.chromo_config.NB_GENES_EACH_PROJECTION}"
        else:


            if self.chromo_config.RELATIVE_ENCODING:
                genes = np.random.rand(self.config.NB_GENES_EACH_CHROMOSOME)
            else:

                list_genes = [
                    np.random.randint(low = 0,
                                      high = network_config.NB_IN_ASSEMBLIES,
                                      size = self.chromo_config.NB_PROJECTIONS_EACH_CHROMOSOME),
                    np.random.randint(low =0 ,
                                      high = 2,
                                      size = self.chromo_config.NB_PROJECTIONS_EACH_CHROMOSOME),

                    np.random.randint(low = 0,
                                      high = network_config.NB_OUT_ASSEMBLIES,
                                      size = self.chromo_config.NB_PROJECTIONS_EACH_CHROMOSOME)
                    ]

                genes = np.concatenate(np.array(list_genes, dtype = int).T, axis = 0)

        return genes


    def get_nb_genes(self) -> np.int64:
        """Retourner le nombre de gènes"""
        return self.genes.shape[0]

    def get_genes(self) -> np.ndarray:
        """Retourner les gènes"""
        return self.genes.copy()
    
    def set_genes(self, genes: np.ndarray):
        """Définir les gènes"""

        if not self.chromo_config.VARIABLE_LENGTH_CHROMOSOME:
            assert len(genes) == self.chromo_config.NB_GENES_EACH_CHROMOSOME

        self.genes = genes
    
    def get_projection(self, projection_idx: int) -> Tuple[int, int, float]:
        """
        Extraire une projection (gène codant une connexion)
        
        Une projection = 3 gènes:
        - Pre-assembly index
        - Post-assembly index
        - Weight
        
        Args:
            projection_idx: Index de la projection (0 à NB_PROJECTIONS-1)
            
        Returns:
            (pre_assembly, post_assembly, weight)
        """
        start_idx = projection_idx * self.chromo_config.NB_GENES_EACH_PROJECTION
        
        # Décoder les gènes
        genes_slice = self.genes[start_idx:start_idx + self.chromo_config.NB_GENES_EACH_PROJECTION]
        
        return genes_slice

    def save_genes(self, target_path=0):

        if target_path==0:
            target_path = os.path.abspath()

        #print(f"saving Chromosome.npy")
        npy_file = os.path.join(target_path, "Chromosome.npy")
        #print(npy_file)
        np.save(npy_file, self.genes)
        #
        # #print(f"saving Chromosome.txt")
        # txt_file = os.path.join(target_path, "Chromosome.txt")
        # #print(txt_file )
        # np.savetxt(txt_file , self.genes)

    def clone(self) -> 'Chromosome':
        """Cloner le chromosome"""
        return Chromosome(self.chromo_config, self.genes.copy())
    
    def __repr__(self):
        return f"Chromosome(genes_len={len(self.genes)}, avg={self.genes.mean():.3f})"
