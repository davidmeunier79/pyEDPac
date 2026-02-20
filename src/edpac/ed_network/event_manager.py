"""
EventManager.py - Équivalent à EventManager.h et CircledList

Gestionnaire d'événements pour simulation event-driven
"""

from collections import defaultdict
from typing import List, Dict, Set, Optional
import heapq
import numpy as np

from ..config.network_config import EventManagerConfig
from ..physiology.dynamic_synapse import DynamicSynapse

class PSPEvent:
    """Événement PSP (Post-Synaptic Potential)"""
    
    def __init__(self, time: int, synapse: 'DynamicSynapse', weight: float):
        """
        Créer un événement PSP
        
        Args:
            time: Temps de l'événement (ms)
            synapse: Synapse source
            weight: Poids du PSP
        """
        self.time = time
        self.synapse = synapse
        self.weight = weight

        # ✅ FIX: Gérer le cas synapse=None pour les inputs injectés
        if synapse is not None:
            self.post_neuron = synapse.post_node
        else:
            self.post_neuron = None  # Sera défini après création

    
    def __lt__(self, other):
        """Comparaison pour heap - ordonne par temps"""
        if self.time != other.time:
            return self.time < other.time
        # Déterminisme: secondaire par ID
        return id(self) < id(other)
    
    def __eq__(self, other):
        return self.time == other.time and self.synapse == other.synapse
    
    def __repr__(self):
        if self.synapse:
            return f"PSPEvent(t={self.time}, S{self.synapse.index}, w={self.weight:.4f})"
        else:
            return f"PSPEvent(t={self.time}, external_input, w={self.weight:.4f})"

class SpikeEvent:
    """Événement spike (action potential)"""
    
    def __init__(self, time: int, neuron: 'SpikingNeuron'):
        """
        Créer un événement spike
        
        Args:
            time: Temps du spike (ms)
            neuron: Neurone qui émet
        """
        self.time = time
        self.neuron = neuron
    
    def __lt__(self, other):
        """Comparaison pour heap"""
        if self.time != other.time:
            return self.time < other.time
        return id(self) < id(other)
    
    def __repr__(self):
        return f"SpikeEvent(t={self.time}, N{self.neuron.index})"


class EventManager:
    """
    Gestionnaire d'événements event-driven
    
    Utilise une queue d'événements (heap) pour simuler efficacement
    un réseau neuronal impulsionnel
    """
    
    def __init__(self, config: EventManagerConfig = None):
        """
        Initialiser le gestionnaire
        
        Args:
            config: Configuration du gestionnaire
        """
        self.config = config or EventManagerConfig()
        
        # File d'événements (min-heap par temps)
        self.event_queue: List[PSPEvent | SpikeEvent] = []
        
        # Temps courant
        self.current_time = 0
        
        # Historique pour statistiques
        self.spike_count = 0
        self.psp_count = 0
        
        # Cache des événements par neurone (pour stats)
        self.events_per_neuron: Dict[int, List] = defaultdict(list)
        
        self.is_empty = True
    
    def reset(self, start_time: int = 0):
        """Réinitialiser le gestionnaire"""
        self.event_queue.clear()
        self.current_time = start_time
        self.spike_count = 0
        self.psp_count = 0
        self.events_per_neuron.clear()
        self.is_empty = True
    
    def schedule_spike(self, time: int, neuron: 'SpikingNeuron'):
        """
        Programmer un spike (émission d'action potential)
        
        Args:
            time: Temps d'émission (ms)
            neuron: Neurone qui va émettre
        """
        if time < self.current_time:
            raise ValueError(f"Cannot schedule event in past (t={time} < current={self.current_time})")
        
        event = SpikeEvent(time, neuron)
        heapq.heappush(self.event_queue, event)
        self.spike_count += 1
        self.is_empty = False
        
        # Debug
        # print(f"  Scheduled spike: {event}")
    
    def schedule_psp(self, synapse: 'DynamicSynapse', spike_time: int):
        """
        Programmer un PSP (potentiel post-synaptique)
        
        Appelé quand un neurone pré-synaptique émet un spike.
        Le PSP arrive au neurone post-synaptique après le délai synaptique.
        
        Args:
            synapse: Synapse transportant le signal
            spike_time: Temps du spike pré-synaptique (ms)
        """
        # Calcul du temps d'arrivée = spike_time + délai
        psp_time = spike_time + synapse.get_delay()
        
        if psp_time < self.current_time:
            raise ValueError(f"PSP event in past (t={psp_time} < current={self.current_time})")
        
        event = PSPEvent(psp_time, synapse, synapse.get_weight())
        heapq.heappush(self.event_queue, event)
        self.psp_count += 1
        self.is_empty = False
        
        # Debug
        # print(f"  Scheduled PSP: {event}")
    
    def run_one_step(self) -> Optional[List]:
        """
        Exécuter une étape de simulation
        
        Traite tous les événements au temps courant, puis avance d'1ms.
        
        Returns:
            Liste des événements traités, ou None si queue vide
        """
        if not self.event_queue:
            self.is_empty = True
            return None
        
        # Récupérer le prochain événement
        next_event = self.event_queue[0]
        self.current_time = next_event.time
        
        # Traiter tous les événements à ce temps
        events_at_current_time = []
        
        while self.event_queue and self.event_queue[0].time == self.current_time:
            event = heapq.heappop(self.event_queue)
            events_at_current_time.append(event)
            
            if isinstance(event, SpikeEvent):
                self._process_spike_event(event)
            elif isinstance(event, PSPEvent):
                self._process_psp_event(event)
        
        # Vérifier si queue vide
        if not self.event_queue:
            self.is_empty = True
        
        return events_at_current_time
    
    def _process_spike_event(self, event: SpikeEvent):
        """Traiter un événement spike"""
        neuron = event.neuron
        time = event.time
        
        # Le neurone a émis un spike
        # Mettre à jour les synapses sortantes
        if hasattr(neuron, 'last_time_of_firing'):
            neuron.last_time_of_firing = time
        
        # Pour chaque synapse sortante, programmer le PSP arrivant
        if hasattr(neuron, 'synapses_out'):
            for synapse in neuron.synapses_out:
                self.schedule_psp(synapse, time)
                
                # Mise à jour STDP pour synapses pré-synaptiques
                if hasattr(synapse, 'update_last_time_of_pre_spike'):
                    synapse.update_last_time_of_pre_spike(time)
    
    def _process_psp_event(self, event: PSPEvent):
        """Traiter un événement PSP"""
        synapse = event.synapse
        post_neuron = event.post_neuron
        time = event.time
        weight = event.weight
        
        # Appliquer l'impact du PSP au neurone post-synaptique
        if post_neuron is not None and hasattr(post_neuron, 'compute_psp_impact'):
            post_neuron.compute_psp_impact(time, weight)

        # Si le neurone génère un spike, le programmer
        if post_neuron is not None and hasattr(post_neuron, 'last_time_of_firing')\
                and post_neuron.last_time_of_firing == time:
            self.schedule_spike(time, post_neuron)

        # Mise à jour STDP pour synapses post-synaptiques
        if synapse is not None and hasattr(synapse, 'update_last_time_of_post_spike'):
            synapse.update_last_time_of_post_spike(time)

    def run_until(self, target_time: int) -> int:
        """
        Exécuter la simulation jusqu'à un temps donné
        
        Args:
            target_time: Temps final (ms)
            
        Returns:
            Nombre d'événements traités
        """
        event_count = 0
        
        while not self.is_empty and self.current_time < target_time:
            events = self.run_one_step()
            if events:
                event_count += len(events)
        
        return event_count
    
    def inject_input(self, neuron: 'SpikingNeuron', time: int, weight: float = 0.1):
        """
        Injecter un input (PSP externe) dans un neurone
        
        Args:
            neuron: Neurone cible
            time: Temps de l'injection (ms)
            weight: Amplitude du PSP
        """
        if time < self.current_time:
            raise ValueError(f"Cannot inject input in past (t={time} < current={self.current_time})")
        
        # Créer un événement PSP direct (pas de synapse réelle)
        event = PSPEvent(time, None, weight)
        event.post_neuron = neuron
        
        heapq.heappush(self.event_queue, event)
        self.is_empty = False
    
    def get_time(self) -> int:
        """Retourner le temps courant"""
        return self.current_time
    
    def get_empty(self) -> bool:
        """Retourner True si queue vide"""
        return self.is_empty
    
    def get_queue_size(self) -> int:
        """Retourner la taille de la queue"""
        return len(self.event_queue)
    
    def get_spike_count(self) -> int:
        """Retourner le nombre de spikes générés"""
        return self.spike_count
    
    def get_psp_count(self) -> int:
        """Retourner le nombre de PSPs traités"""
        return self.psp_count
    
    def __repr__(self):
        return f"EventManager(t={self.current_time}, queue={len(self.event_queue)}, spikes={self.spike_count}, psps={self.psp_count})"
