from visualizer import BaseVisualizer

class VisuZoo:
    def __init__(self, visualizer: BaseVisualizer):
        self.viz = visualizer
        self.agents = [{"x": 0, "y": 0, "color": 'r'} for _ in range(10)]

    def update_and_draw(self):
        self.viz.clear_canvas() # Clear previous frame
        for a in self.agents:
            # Move agent logic here...
            self.viz.draw_agent(a['x'], a['y'], color=a['color'])
