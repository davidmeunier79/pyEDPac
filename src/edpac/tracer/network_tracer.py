import os
import numpy as np

import matplotlib
matplotlib.use('Agg') # Must be called before importing pyplot

from matplotlib import pyplot as plt

from .tracer import Tracer

class NetworkTracer(Tracer):
    def __init__(self, network):
        self.network = network

        # Scaling parameters (adjust based on your neuron model constants)
        #self.v_min = neuron.config.RESTING_POTENTIAL
        #self.v_max = neuron.config.THRESHOLD_REF    # Usually the threshold

        super().__init__()

    def record(self, time, spike_neuron_ids):
        """Samples the current membrane potential."""
        # Shift history to the left and add new value

        self.history.append((time, spike_neuron_ids)) # Accessing the potential of the EDNeuron

    def plot(self, target_dir = 0):
        """
        Plotting with matplotlib
        """

        if not target_dir:
            target_dir = os.path.abspath("")

        if len(self.history)==0:
            return

        max_time = self.history[-1][0]

        spike_array = np.zeros (shape = (max_time+1, self.network.get_nb_neurons()))

        for time, spike_ids in self.history:
            spike_array[time, spike_ids] = 1

        fig = plt.figure()

        plt.imshow(spike_array.T, aspect='auto', cmap='binary', origin='lower')

        plt.xlabel("Time Steps")
        plt.ylabel("Neuron Index")
        plt.title("Network Spiking Activity")
#
        plt.tight_layout()
#     plt.savefig(filename, dpi=300)
#     plt.close() # Closes the figure to free up memory
#
        file_path = os.path.join(target_dir, "Network_spikes.eps")

        fig.savefig(file_path, dpi=300)
        assert os.path.exists(file_path), \
            "Error with plotting {}".format(plot_signals_file)

        fig.close()


