
class Projection():

    _link_count = 0

    def __init__(self, pre_node=None, post_node=None, nature = None):

        self.pre_node = pre_node      # Nœud source
        self.post_node = post_node    # Nœud cible

        self.nature = nature
