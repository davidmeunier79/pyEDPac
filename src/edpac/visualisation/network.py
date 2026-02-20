
class Network:
    def __init__(self, visualizer=None):
        self.viz = visualizer

    def draw(self, neurons, synapses):
        if self.viz:
            self.viz.clear_canvas()
            # Draw Synapses (Lines)
            for s in synapses:
                self.viz.draw_line(s.pre.x, s.pre.y, s.post.x, s.post.y, color='gray')
            # Draw Neurons (Points)
            for n in neurons:
                color = 'yellow' if n.is_firing else 'blue'
                self.viz.draw_point(n.x, n.y, size=12, color=color)
            self.viz.refresh()
