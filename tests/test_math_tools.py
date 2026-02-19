"""
test_math_tools.py

Tests unitaires pour NeuronMathTools et SynapseMathTools
"""

import pytest
import sys
import numpy as np
sys.path.insert(0, '../src')

from edpac.math_tools.neuron_math import NeuronMathTools, SynapseMathTools
from edpac.config.physiology_config import NeuronConfig, SynapseConfig


class TestNeuronMathTools:
    """Tests pour NeuronMathTools"""
    
    def setup_method(self):
        """Setup avant chaque test"""
        self.math_tools = NeuronMathTools()
    
    def test_exponential_decay_basic(self):
        """Décroissance exponentielle basique"""
        # V(t) = 1.0 * exp(-10 / 50) ≈ 0.8187
        result = self.math_tools.exponential_decay(1.0, 50.0, 10.0)
        
        expected = np.exp(-10.0 / 50.0)
        assert abs(result - expected) < 1e-6
    
    def test_exponential_decay_full_decay(self):
        """Décroissance complète après 5*tau"""
        # Après 5*tau, la valeur devrait être pratiquement zéro
        result = self.math_tools.exponential_decay(1.0, 50.0, 250.0)
        
        # exp(-250/50) = exp(-5) ≈ 0.0067
        assert result < 0.01
    
    def test_exponential_decay_zero_time(self):
        """Pas de décroissance à t=0"""
        result = self.math_tools.exponential_decay(1.0, 50.0, 0.0)
        
        assert result == pytest.approx(1.0)
    
    def test_exponential_decay_zero_tau_returns_zero(self):
        """tau=0 retourne 0"""
        result = self.math_tools.exponential_decay(1.0, 0.0, 10.0)
        
        assert result == 0.0
    
    def test_linear_decay_basic(self):
        """Décroissance linéaire basique"""
        result = self.math_tools.linear_decay(1.0, 0.1, 5.0)
        
        # 1.0 - 0.1*5 = 0.5
        assert result == pytest.approx(0.5)
    
    def test_linear_decay_clamps_to_zero(self):
        """Clamp à zéro si décroissance > valeur"""
        result = self.math_tools.linear_decay(1.0, 0.1, 20.0)
        
        # 1.0 - 0.1*20 = -1.0 -> clamped to 0.0
        assert result == 0.0
    
    def test_sigmoid_at_threshold(self):
        """Sigmoïde à threshold = 0.5"""
        result = self.math_tools.sigmoid(0.0, gain=1.0, threshold=0.0)
        
        # 1 / (1 + exp(0)) = 1 / 2 = 0.5
        assert result == pytest.approx(0.5)
    
    def test_sigmoid_high_value(self):
        """Sigmoïde pour haute valeur ≈ 1"""
        result = self.math_tools.sigmoid(10.0, gain=1.0, threshold=0.0)
        
        assert result > 0.99
    
    def test_sigmoid_low_value(self):
        """Sigmoïde pour basse valeur ≈ 0"""
        result = self.math_tools.sigmoid(-10.0, gain=1.0, threshold=0.0)
        
        assert result < 0.01
    
    def test_threshold_function_above_threshold(self):
        """Threshold True si au-dessus"""
        result = self.math_tools.threshold_function(0.5, threshold=0.0)
        
        assert result is True
    
    def test_threshold_function_below_threshold(self):
        """Threshold False si en-dessous"""
        result = self.math_tools.threshold_function(-0.5, threshold=0.0)
        
        assert result is False
    
    def test_threshold_function_at_threshold(self):
        """Threshold True si égal (>=)"""
        result = self.math_tools.threshold_function(0.0, threshold=0.0)
        
        assert result is True


class TestSynapseMathTools:
    """Tests pour SynapseMathTools (STDP)"""
    
    def setup_method(self):
        """Setup avant chaque test"""
        config = SynapseConfig(DELAY=10, INHIBITORY_DELAY=10)
        self.math_tools = SynapseMathTools(config)
    
    def test_excit_temporal_window_potentiation(self):
        """STDP potentiation: post après pré"""
        # Si post-spike arrive 5ms après pré-spike
        delta_weight = self.math_tools.excit_temporal_window(5)
        
        # Devrait être positif (potentiation)
        assert delta_weight > 0
        # Pente = 1.0 / 10 * 5 = 0.5
        assert delta_weight == pytest.approx(0.5)
    
    def test_excit_temporal_window_depression(self):
        """STDP dépression: pré après post"""
        # Si pré-spike arrive 5ms après post-spike (dt < 0)
        delta_weight = self.math_tools.excit_temporal_window(-5)
        
        # Devrait être négatif (dépression)
        assert delta_weight < 0
    
    def test_excit_temporal_window_zero_delay(self):
        """STDP à dt=0"""
        delta_weight = self.math_tools.excit_temporal_window(0)
        
        # À dt=0, le résultat dépend de la fenêtre
        assert isinstance(delta_weight, (int, float))
    
    def test_excit_temporal_window_outside_window(self):
        """STDP en-dehors de la fenêtre"""
        # Très loin dans le passé
        delta_weight = self.math_tools.excit_temporal_window(-100)
        
        assert delta_weight == 0.0
        
        # Très loin dans le futur
        delta_weight = self.math_tools.excit_temporal_window(100)
        
        assert delta_weight == 0.0
    
    def test_inhib_temporal_window_inside_window(self):
        """STDP inhibiteur dans la fenêtre"""
        delta_weight = self.math_tools.inhib_temporal_window(20)
        
        # Devrait être positif dans la fenêtre
        assert delta_weight > 0
    
    def test_inhib_temporal_window_outside_window(self):
        """STDP inhibiteur en-dehors de la fenêtre"""
        delta_weight = self.math_tools.inhib_temporal_window(100)
        
        # Dépression en-dehors
        assert delta_weight < 0
    
    def test_apply_stdp_multiplicative_potentiation(self):
        """STDP multiplicatif - potentiation"""
        weight = 0.5
        delta_weight = 0.5  # Positif
        alpha = 0.01
        
        new_weight, real_delta = self.math_tools.apply_stdp_multiplicative(
            weight, delta_weight, alpha, is_potentiation=True
        )
        
        # new_weight = 0.5 + 0.01*0.5*(1-0.5) = 0.5 + 0.0025 = 0.5025
        expected_delta = 0.01 * 0.5 * 0.5
        expected_weight = 0.5 + expected_delta
        
        assert new_weight == pytest.approx(expected_weight)
        assert real_delta == pytest.approx(expected_delta)
    
    def test_apply_stdp_multiplicative_depression(self):
        """STDP multiplicatif - dépression"""
        weight = 0.5
        delta_weight = -0.5  # Négatif
        alpha = 0.01
        
        new_weight, real_delta = self.math_tools.apply_stdp_multiplicative(
            weight, delta_weight, alpha, is_potentiation=False
        )
        
        # new_weight = 0.5 + 0.01*(-0.5)*0.5 = 0.5 - 0.0025 = 0.4975
        expected_delta = 0.01 * (-0.5) * 0.5
        expected_weight = 0.5 + expected_delta
        
        assert new_weight == pytest.approx(expected_weight)
        assert real_delta == pytest.approx(expected_delta)
    
    def test_apply_stdp_multiplicative_clamps_to_one(self):
        """STDP multiplicatif - clamp à 1.0"""
        weight = 0.99
        delta_weight = 10.0  # Très positif
        alpha = 1.0  # Alpha élevé
        
        new_weight, _ = self.math_tools.apply_stdp_multiplicative(
            weight, delta_weight, alpha, is_potentiation=True
        )
        
        # Devrait être clamped à 1.0
        assert new_weight == pytest.approx(1.0)
    
    def test_apply_stdp_multiplicative_clamps_to_zero(self):
        """STDP multiplicatif - clamp à 0.0"""
        weight = 0.01
        delta_weight = -10.0  # Très négatif
        alpha = 1.0  # Alpha élevé
        
        new_weight, _ = self.math_tools.apply_stdp_multiplicative(
            weight, delta_weight, alpha, is_potentiation=False
        )
        
        # Devrait être clamped à 0.0
        assert new_weight == pytest.approx(0.0)
    
    def test_apply_stdp_multiplicative_zero_delta(self):
        """STDP multiplicatif - delta=0 ne change rien"""
        weight = 0.5
        
        new_weight, real_delta = self.math_tools.apply_stdp_multiplicative(
            weight, 0.0, 0.01, is_potentiation=True
        )
        
        assert new_weight == weight
        assert real_delta == 0.0
    
    def test_random_weight(self):
        """Générer un poids aléatoire"""
        np.random.seed(42)
        
        weight = SynapseMathTools.random_weight(base_weight=0.5)
        
        # Devrait être entre 0 et 1
        assert 0.0 <= weight <= 1.0
        # Devrait être à peu près proche de 0.5
        assert abs(weight - 0.5) < 1.0  # Loose check
    
    def test_random_delay(self):
        """Générer un délai aléatoire"""
        delay = SynapseMathTools.random_delay(max_delay=10)
        
        # Devrait être entre 1 et max_delay
        assert 1 <= delay <= 10


class TestSTDPIntegration:
    """Tests d'intégration pour STDP"""
    
    def test_stdp_window_continuity(self):
        """La fenêtre STDP doit être continue"""
        math_tools = SynapseMathTools()
        
        # Tester à plusieurs points
        times = np.linspace(-25, 25, 51)
        deltas = [math_tools.excit_temporal_window(int(t)) for t in times]
        
        # Devrait y avoir une transition douce
        assert max(deltas) > 0  # Potentiation existe
        assert min(deltas) < 0  # Dépression existe
    
    def test_learning_sequence(self):
        """Tester une séquence d'apprentissage"""
        math_tools = SynapseMathTools()
        
        weight = 0.5
        alpha = 0.1
        
        # Plusieurs paires spike pré/post avec délais positifs
        temporal_differences = [5, 5, 5]  # Potentiation
        
        for td in temporal_differences:
            delta_w = math_tools.excit_temporal_window(td)
            weight, _ = math_tools.apply_stdp_multiplicative(
                weight, delta_w, alpha, is_potentiation=True
            )
        
        # Le poids devrait augmenter
        assert weight > 0.5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])