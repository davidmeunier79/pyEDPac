from visualizer import BaseVisualizer

class Network:
    def __init__(self, visualizer: BaseVisualizer):
        self.viz = visualizer

    def draw_network(self, adjacency_matrix, positions):
        self.viz.clear_canvas()
        # Draw connections (synapses)
        for i, row in enumerate(adjacency_matrix):
            for j, weight in enumerate(row):
                if weight > 0:
                    p1 = positions[i]
                    p2 = positions[j]
                    self.viz.draw_connection(p1[0], p1[1], p2[0], p2[1], weight=weight)

        # Draw nodes (neurons)
        for pos in positions:
            self.viz.draw_agent(pos[0], pos[1], size=10, color='g')
