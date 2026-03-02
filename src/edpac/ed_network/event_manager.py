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
            return f"PSPEvent(t={self.time}, S-{self.synapse.id}, w={self.weight:.4f})"
        else:
            return f"PSPEvent(t={self.time}, external_input, w={self.weight:.4f})"

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
        self.event_queue: List[PSPEvent] = []

        # Temps courant
        self.current_time = 0

        # Historique pour statistiques
        self.psp_count = 0

        self.is_empty = True

    def get_events(self):

        return self.event_queue

    def get_nb_events(self):

        return len(self.event_queue)

    def reset(self, start_time: int = 0):
        """Réinitialiser le gestionnaire"""
        self.event_queue.clear()
        self.current_time = start_time
        self.psp_count = 0
        self.is_empty = True

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
        #print("spike_time: ", spike_time, " -> psp_time: ", psp_time)

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

        print("time: ",self.current_time)

        # Traiter tous les événements à ce temps
        events_at_current_time = []

        while self.event_queue and (self.event_queue[0].time == self.current_time):
            #print("event queue:", len(self.event_queue))

            event = heapq.heappop(self.event_queue)
            #events_at_current_time.append(event)
            #print(event)

            neuron_id = self._process_psp_event(event)

            if neuron_id != -1:
                events_at_current_time.append(neuron_id)

        # Vérifier si queue vide
        if not self.event_queue:
            self.is_empty = True
        #print( events_at_current_time)

        return events_at_current_time

    def _process_psp_event(self, event: PSPEvent):
        """Traiter un événement PSP"""
        synapse = event.synapse
        post_neuron = event.post_neuron
        time = event.time
        weight = event.weight

        # Appliquer l'impact du PSP au neurone post-synaptique
        if post_neuron.compute_psp_impact(time, weight):
            return post_neuron.id
        else:
            return -1
        #
        # # Si le neurone génère un spike, le programmer
        # if post_neuron is not None and hasattr(post_neuron, 'last_time_of_firing')\
        #         and post_neuron.last_time_of_firing == time:
        #     self.schedule_spike(time, post_neuron)
        #
        # # Mise à jour STDP pour synapses post-synaptiques
        # if synapse is not None and hasattr(synapse, 'update_last_time_of_post_spike'):
        #     synapse.update_last_time_of_post_spike(time)

    def run_until(self, target_time: int) -> int:
        """
        Exécuter la simulation jusqu'à un temps donné

        Args:
            target_time: Temps final (ms)

        Returns:
            Nombre d'événements traités
        """
        event_count = 0

        print("init time: ", self.current_time)

        while not self.is_empty and self.current_time < target_time:

            print("time: ", self.current_time)

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


