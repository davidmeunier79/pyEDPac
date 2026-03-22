import os
import numpy as np
from matplotlib import pyplot as plt


from .tracer import Tracer

class NeuronTracer(Tracer):
    def __init__(self, neuron):
        self.neuron = neuron

        # Scaling parameters (adjust based on your neuron model constants)
        #self.v_min = neuron.config.RESTING_POTENTIAL
        #self.v_max = neuron.config.THRESHOLD_REF    # Usually the threshold

        super().__init__()

    def record(self, time):
        """Samples the current membrane potential."""
        # Shift history to the left and add new value
        self.history.append((time, self.neuron.membrane_potential, self.neuron.threshold_potential)) # Accessing the potential of the EDNeuron

    def plot(self, target_dir = 0):
        """
        Plotting with matplotlib
        """

        if not target_dir:
            target_dir = os.path.abspath("")

        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)

        arr = np.array(self.history)
        print(arr)
        print(arr.shape)

        ax.plot(arr[:,0], arr[:,1], color = "blue")

        ax.plot(arr[:,0], arr[:,1], color = "green")

        ax.grid()

        plot_file = f"Neuron_Potential_{self.neuron.id}.png"
        fig.savefig(os.path.join(target_dir, plot_file))
        assert os.path.exists(plot_file), \
            "Error with plotting {}".format(plot_signals_file)


