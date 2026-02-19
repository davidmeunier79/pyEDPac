"""
Link.py - Équivalent à Link.h (classe de base pour connexions)
"""

class Link:
    """Classe de base pour les liens d'un graphe orienté"""
    
    _link_count = 0
    
    def __init__(self, pre_node=None, post_node=None):
        """
        Initialiser un lien entre deux nœuds
        
        Args:
            pre_node: Nœud pré-synaptique (source)
            post_node: Nœud post-synaptique (cible)
        """
        self.index = Link._link_count
        Link._link_count += 1
        
        self.pre_node = pre_node      # Nœud source
        self.post_node = post_node    # Nœud cible
        
        # Enregistrer auprès des nœuds
        if pre_node is not None:
            pre_node.add_outgoing_link(self)
        if post_node is not None:
            post_node.add_incoming_link(self)
    
    @staticmethod
    def reset_count():
        """Réinitialiser le compteur de liens"""
        Link._link_count = 0
    
    def __repr__(self):
        return f"Link({self.index}: {self.pre_node.index} -> {self.post_node.index})"