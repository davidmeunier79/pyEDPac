import os
import numpy as np
from matplotlib import pyplot as plt


from .tracer import Tracer

class SynapseTracer(Tracer):
    def __init__(self, synapse):
        self.synapse = synapse

        super().__init__()

    def record(self, time):
        """Samples the current membrane potential."""
        # Shift history to the left and add new value
        self.history.append((time, self.synapse.weight, self.synapse.last_time_of_post_spike, self.synapse.last_time_of_pre_spike)) # Accessing the potential of the EDNeuron

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

        ax.grid()

        plot_file = f"Weight_{self.synapse.id}.png"
        fig.savefig(os.path.join(target_dir, plot_file))
        assert os.path.exists(plot_file), \
            "Error with plotting {}".format(plot_signals_file)


