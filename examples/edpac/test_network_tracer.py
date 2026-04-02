import os
import sys
sys.path.insert(0, '../src')

import numpy as np

import time

from edpac.ed_network.ed_synapse import EDSynapse


from edpac.ed_network.evo_network import EvoNetwork

from edpac.config.constants import *
from edpac.config.physiology_config import NeuronConfig


from edpac.tracer.network_tracer import NetworkTracer
from edpac.genetic_algorithm.chromosome import Chromosome

from edpac.config.constants import *
from edpac.config.ga_config import ChromosomeConfig

def main():

    ################################### Chromosome ################################

    # Create objects
    chromo_config = ChromosomeConfig()
    chromo_config.VARIABLE_LENGTH_CHROMOSOME=False
    chromo_config.NB_PROJECTIONS_EACH_CHROMOSOME = 720  # Nombre de projections
    chromo_config.NB_GENES_EACH_CHROMOSOME = chromo_config.NB_PROJECTIONS_EACH_CHROMOSOME*chromo_config.NB_GENES_EACH_PROJECTION

    chromosome = Chromosome(config = chromo_config)


    ################################### EvoNetwork ################################

    net = EvoNetwork(chromosome)

    print(net)

    spike_neuron_ids = net.initialize_inputs()

    network_tracer = NetworkTracer(net)
    network_tracer.record(0, spike_neuron_ids)

    MAX_TIME = 1000

    while EDSynapse.event_manager.get_nb_events() and EDSynapse.event_manager.get_time() < MAX_TIME:

        current_time = EDSynapse.event_manager.get_time()

        net.init_output_patterns()

        while (EDSynapse.event_manager.get_time() - current_time) < MINIMAL_TIME and  EDSynapse.event_manager.get_nb_events():
            #
            # if EDSynapse.event_manager.get_time() % 50 == 0:
            #     print(f"{EDSynapse.event_manager.get_time()}: Neuron 0 spikes ")
            #     spike_neuron_ids = net.initialize_inputs(EDSynapse.event_manager.get_time())
            #
            #     network_tracer.record(EDSynapse.event_manager.get_time(), spike_neuron_ids)

            spike_neuron_ids = EDSynapse.event_manager.run_one_step()

            if spike_neuron_ids is not None:
                network_tracer.record(EDSynapse.event_manager.get_time(), spike_neuron_ids)

            else:
                print("No spikes in event manager")

            print(EDSynapse.event_manager.get_time(), EDSynapse.event_manager.get_nb_events())

        output_patterns = net.get_output_patterns()

    else:
        print("No more events in event manager time > MAX_TIME {MAX_TIME}, breaking")

    network_tracer.plot()

if __name__ == "__main__":
    main()
