class Zoo:
    def __init__(self, visualizer=None):
        self.viz = visualizer
        self.animals = [] # List of animal objects with x, y

    def draw(self):
        if self.viz:
            self.viz.clear_canvas()
            for animal in self.animals:
                self.viz.draw_point(animal.x, animal.y, color='r', symbol='t') # 't' for triangle
            self.viz.refresh()
