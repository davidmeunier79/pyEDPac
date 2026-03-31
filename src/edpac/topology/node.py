"""
Node.py - Équivalent à Node.h (classe de base pour graphe)
"""

class Node:
    """Classe de base pour les nœuds d'un graphe orienté"""
    
    _node_count = 0
    
    def __init__(self):
        """Initialiser un nœud"""
        self.id = Node._node_count
        Node._node_count += 1

        self.outgoing_links = []  # Liens sortants (post-synaptiques)
        self.incoming_links = []  # Liens entrants (pré-synaptiques)
    
    def add_outgoing_link(self, link):
        """Ajouter un lien sortant"""
        self.outgoing_links.append(link)
    
    def add_incoming_link(self, link):
        """Ajouter un lien entrant"""
        self.incoming_links.append(link)
    
    @staticmethod
    def reset_count():
        """Réinitialiser le compteur de nœuds"""
        Node._node_count = 0
    
    def __repr__(self):
        return f"Node({self.id})"
