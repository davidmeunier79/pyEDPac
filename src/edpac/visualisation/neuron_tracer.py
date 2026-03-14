import numpy as np

class NeuronTracer:
    def __init__(self, neuron, buffer_size=100, height=100):
        self.neuron = neuron
        self.buffer_size = buffer_size
        self.height = height
        # Store the history of membrane potentials
        self.history = []

        # Scaling parameters (adjust based on your neuron model constants)
        self.v_min = neuron.config.RESTING_POTENTIAL
        self.v_max = neuron.config.THRESHOLD_REF    # Usually the threshold

    def record(self, time):
        """Samples the current membrane potential."""
        # Shift history to the left and add new value
        self.history.append((time, self.neuron.membrane_potential)) # Accessing the potential of the EDNeuron

    def draw_trace(self, visualizer, color=(0, 255, 255)):
        """Draws the potential wave using the PixelVisualizer's draw_line."""
        # Calculate horizontal spacing

        for i in range(len(self.history) - 1):
            # Normalize V to Y coordinates
            y1 = self._map_v_to_y(self.history[i][1])
            y2 = self._map_v_to_y(self.history[i+1][1])

            x1 = self.history[i][1]
            x2 = self.history[i+1][1]

            visualizer.draw_line((x1, y1), (x2, y2), color)

    def _map_v_to_y(self, v):
        """Maps membrane potential to pixel Y-coordinate."""
        # Simple linear scaling: (v - v_min) / (v_max - v_min)
        norm_v = (v - self.v_min) / (self.v_max - self.v_min)
        norm_v = np.clip(norm_v, 0, 1)
        # Invert because Y=0 is top in PixelVisualizer
        return self.height - (norm_v * (self.height - 5)) - 2
