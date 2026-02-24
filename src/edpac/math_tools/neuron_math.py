"""
NeuronMath.py - Équivalent à NeuronMathTools.h

Modèles mathématiques pour neurones et STDP (Spike-Timing-Dependent Plasticity)
"""

import numpy as np
from typing import Tuple
from ..config.physiology_config import NeuronConfig, SynapseConfig

class NeuronMathTools:
    """Outils mathématiques pour les neurones"""
    
    def __init__(self, config: NeuronConfig = None):
        """Initialiser avec configuration"""
        self.config = config or NeuronConfig()
        
        # Constantes pour décroissance exponentielle
        self.MEMBRANE_TIME_CONSTANT = 50.0  # ms (tau)
        self.SYNAPSE_TIME_CONSTANT = 10.0   # ms
    
    @staticmethod
    def exponential_decay(value: float, time_constant: float, elapsed_time: float) -> float:
        """
        Décroissance exponentielle
        
        V(t) = V(0) * exp(-t / tau)
        
        Args:
            value: Valeur initiale
            time_constant: Constante de temps (tau en ms)
            elapsed_time: Temps écoulé (ms)
            
        Returns:
            Valeur décroissante
        """
        if time_constant <= 0:
            return 0.0
        
        decay_factor = np.exp(-elapsed_time / time_constant)
        return value * decay_factor
    
    @staticmethod
    def linear_decay(value: float, rate: float, elapsed_time: float) -> float:
        """
        Décroissance linéaire
        
        V(t) = V(0) - rate * t
        
        Args:
            value: Valeur initiale
            rate: Taux de décroissance (par ms)
            elapsed_time: Temps écoulé (ms)
            
        Returns:
            Valeur décroissante
        """
        decay = value - rate * elapsed_time
        return max(0.0, decay)
    
    @staticmethod
    def sigmoid(x: float, gain: float = 1.0, threshold: float = 0.0) -> float:
        """
        Fonction sigmoïde
        
        f(x) = 1 / (1 + exp(-gain * (x - threshold)))
        
        Args:
            x: Valeur d'entrée
            gain: Gain (pente)
            threshold: Seuil
            
        Returns:
            Valeur sigmoïde (entre 0 et 1)
        """
        return 1.0 / (1.0 + np.exp(-gain * (x - threshold)))
    
    @staticmethod
    def threshold_function(potential: float, threshold: float) -> bool:
        """
        Fonction seuil simple (Heaviside)
        
        Returns True si potential >= threshold
        
        Args:
            potential: Potentiel courant
            threshold: Seuil
            
        Returns:
            True si dépassement de seuil
        """
        return potential >= threshold

class SynapseMathTools:
    """Outils mathématiques pour synapses (STDP)"""
    
    def __init__(self, config: SynapseConfig = None):
        """Initialiser avec configuration"""
        self.config = config or SynapseConfig()
        
        # Paramètres STDP
        self.DELAY = config.DELAY
        self.INHIBITORY_DELAY = config.INHIBITORY_DELAY
    
    def excit_temporal_window(self, temporal_difference: int) -> float:
        """
        Fenêtre STDP pour synapses excitatrices (Continuous Hebbian)
        
        Basée sur: "Enhancement of synchrony via STDP synapses", Nowotny, 2003
        
        La modification de poids dépend du décalage temporel:
        - post_spike - pre_spike (temporal_difference > 0): potentiation
        - pre_spike - post_spike (temporal_difference < 0): dépression
        
        Args:
            temporal_difference: t_post - t_pre (en ms)
            
        Returns:
            Facteur de modification du poids
        """
        # Fenêtre continue
        delay = self.DELAY
        inhib_delay = self.INHIBITORY_DELAY
        
        if temporal_difference < -(delay + inhib_delay):
            # Trop loin dans le passé
            return 0.0
        
        elif -(delay + inhib_delay) <= temporal_difference < 0:
            # Pré-synaptique avant post-synaptique: DÉPRESSION
            # Pente négative, maximum à t=0
            delta_weight = -1.0 / (delay + inhib_delay) * temporal_difference
            return delta_weight
        
        elif 0 <= temporal_difference < delay:
            # Post-synaptique après pré-synaptique: POTENTIATION
            # Pente positive, décroissante
            delta_weight = 1.0 * temporal_difference / delay
            return delta_weight
        
        elif delay <= temporal_difference < (delay + inhib_delay):
            # Trop loin après pré: DÉPRESSION
            delta_weight = -1.0 / inhib_delay * (temporal_difference - (delay + inhib_delay))
            return delta_weight
        
        else:
            # Trop loin dans le futur
            return 0.0
    
    def inhib_temporal_window(self, temporal_difference: int) -> float:
        """
        Fenêtre STDP pour synapses inhibitoires
        
        Modèle plus simple: fenêtre large avec base dépressive
        
        Args:
            temporal_difference: t_post - t_pre (en ms)
            
        Returns:
            Facteur de modification du poids
        """
        stdp_time_length = 50  # ms (configurable)
        depression_strength = 0.1  # (configurable)
        
        if -stdp_time_length <= temporal_difference <= stdp_time_length:
            # Fenêtre STDP active
            return 1.0
        else:
            # Hors fenêtre: dépression
            return -depression_strength
    
    def apply_stdp_multiplicative(
        self, 
        weight: float, 
        delta_weight: float, 
        alpha: float,
        is_potentiation: bool
    ) -> Tuple[float, float]:
        """
        Appliquer la règle multiplicative STDP
        
        Règle multiplicative: w_new = w + alpha * delta_w * (1-w) [potentiation]
                                      w + alpha * delta_w * w       [dépression]
        
        Évite les dépassements de [0, 1]
        
        Args:
            weight: Poids courant
            delta_weight: Facteur STDP (de la fenêtre temporelle)
            alpha: Coefficient d'apprentissage
            is_potentiation: True si potentiation, False si dépression
            
        Returns:
            (nouveau_poids, changement_réel)
        """
        if delta_weight == 0:
            return weight, 0.0
        
        if is_potentiation:
            # Augmenter le poids, limiter à 1.0
            real_delta = alpha * delta_weight * (1.0 - weight)
        else:
            # Diminuer le poids, limiter à 0.0
            real_delta = alpha * delta_weight * weight
        
        new_weight = weight + real_delta
        # Clamp to [0, 1]
        new_weight = np.clip(new_weight, 0.0, 1.0)
        
        return new_weight, real_delta
    
    @staticmethod
    def random_weight(base_weight: float = 0.5) -> float:
        """Générer un poids initial aléatoire"""
        sign = np.random.choice([-1, 1])
        return base_weight * (1.0 + sign * np.random.random())
    
    @staticmethod
    def random_delay(max_delay: int = 10) -> int:
        """Générer un délai aléatoire"""
        return np.random.randint(1, max_delay + 1)
