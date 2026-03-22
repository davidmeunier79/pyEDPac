"""
Simple Network Example

Démonstration de création et simulation d'un petit réseau neuronal
"""

import sys
sys.path.insert(0, '../src')

from edpac import (
    Neuron, 
    EDNeuron,
    EDSynapse,
    SynapseConfig,
    NeuronConfig
)



from edpac.ed_network.event_manager import EventManager

from edpac.tracer.neuron_tracer import NeuronTracer
from edpac.tracer.synapse_tracer import SynapseTracer



def test_one_synapse():


    EDSynapse.set_event_manager(EventManager())

    # Configuration
    neuron_config = NeuronConfig()
    neuron_config.THRESHOLD_REF = 1.0

    # Créer 3 neurones
    neurons = [EDNeuron(neuron_config) for _ in range(2)]
    print(f"Created {len(neurons)} neurons")

    # Connecter les neurones
    synapse_config = SynapseConfig()

    synapse_config.WEIGHT = 0.5  # Poids fort
    synapse_config.INITIAL_WEIGHT_MODE = "fixed"

    # N0 -> N1
    syn1 = EDSynapse(neurons[0], neurons[1], synapse_config)

    print("\nNetwork structure:")
    for neuron in neurons:
        print(f"  {neuron}: {len(neuron.incoming_links)} inputs, {len(neuron.outgoing_links)} outputs")


    # NeuronTracer
    neuron_tracer = NeuronTracer(neurons[1])
    neuron_tracer.record(0)

    # SynapseTracer
    synapse_tracer = SynapseTracer(syn1)
    synapse_tracer.record(0)

    # Simuler quelques impulsions
    print("\n--- Simulation ---")
    #
    #for i in range(10):
    #    neurons[0].emit_spike(i * 5)

    #     print(f"Init: Neuron 0 spikes: {i*10}")

    MAX_TIME = 200

    time = 0

    print(f"{time}: Neuron 0 spikes ")
    neurons[0].emit_spike(time)

    while time < MAX_TIME :

        print ("Queue: ", EDSynapse.event_manager.event_queue)
        print("Nb events: ", EDSynapse.event_manager.get_nb_events())

        if time == EDSynapse.event_manager.get_time():

            print("*** matching time: ", time)

            spike_neuron_ids = EDSynapse.event_manager.run_one_step()

            if len(spike_neuron_ids):
                print("Spike emissions by : ", spike_neuron_ids, " at time ", time)
        else:

            print("*** time: ", time, " != ", EDSynapse.event_manager.get_time())



        if time % 5 == 0:
            print(f"{time}: Neuron 0 spikes ")
            neurons[0].emit_spike(time)


        #time = EDSynapse.event_manager.get_time()

        neuron_tracer.record(time)
        synapse_tracer.record(time)

        time += 1




    print(f"Breaking because nb_events= {EDSynapse.event_manager.get_nb_events()} or {time} > MAX_TIME {MAX_TIME}")

    print("NeuronTracer:")

    neuron_tracer.plot()

    print("synapseTracer:")

    synapse_tracer.plot()


def test_two_input_neurons():


    EDSynapse.set_event_manager(EventManager())

    # Configuration
    neuron_config = NeuronConfig()
    neuron_config.THRESHOLD_REF = 1.0

    # Créer 3 neurones
    neurons = [EDNeuron(neuron_config) for _ in range(3)]
    print(f"Created {len(neurons)} neurons")

    # Connecter les neurones
    synapse_config = SynapseConfig()

    synapse_config.WEIGHT = 0.5  # Poids fort
    synapse_config.INITIAL_WEIGHT_MODE = "fixed"

    # N0 -> N1
    syn1 = EDSynapse(neurons[0], neurons[1], synapse_config)

    syn2 = EDSynapse(neurons[2], neurons[1], synapse_config)

    print("\nNetwork structure:")
    for neuron in neurons:
        print(f"  {neuron}: {len(neuron.incoming_links)} inputs, {len(neuron.outgoing_links)} outputs")


    # NeuronTracer
    neuron_tracer = NeuronTracer(neurons[1])
    neuron_tracer.record(0)

    # SynapseTracer
    synapse_tracer = SynapseTracer(syn1)
    synapse_tracer.record(0)

    synapse_tracer2 = SynapseTracer(syn2)
    synapse_tracer2.record(0)

    # Simuler quelques impulsions
    print("\n--- Simulation ---")
    #
    #for i in range(10):
    #    neurons[0].emit_spike(i * 5)

    #     print(f"Init: Neuron 0 spikes: {i*10}")

    MAX_TIME = 100

    time = 0

    print(f"{time}: Neuron 0 spikes ")
    neurons[0].emit_spike(time)

    while time < MAX_TIME :

        print ("Queue: ", EDSynapse.event_manager.event_queue)
        print("Nb events: ", EDSynapse.event_manager.get_nb_events())

        if time == EDSynapse.event_manager.get_time():

            print("*** matching time: ", time)

            spike_neuron_ids = EDSynapse.event_manager.run_one_step()

            if len(spike_neuron_ids):
                print("Spike emissions by : ", spike_neuron_ids, " at time ", time)
        else:

            print("*** time: ", time, " != ", EDSynapse.event_manager.get_time())



        if time % 20 == 0:
            print(f"{time}: Neuron 0 spikes ")
            neurons[0].emit_spike(time)


        #time = EDSynapse.event_manager.get_time()

        neuron_tracer.record(time)
        synapse_tracer.record(time)
        synapse_tracer2.record(time)

        time += 1


    MAX_TIME = 200

    print(f"{time}: Neuron 0 spikes ")
    neurons[0].emit_spike(time)

    while time < MAX_TIME :

        print ("Queue: ", EDSynapse.event_manager.event_queue)
        print("Nb events: ", EDSynapse.event_manager.get_nb_events())

        if time == EDSynapse.event_manager.get_time():

            print("*** matching time: ", time)

            spike_neuron_ids = EDSynapse.event_manager.run_one_step()

            if len(spike_neuron_ids):
                print("Spike emissions by : ", spike_neuron_ids, " at time ", time)
        else:

            print("*** time: ", time, " != ", EDSynapse.event_manager.get_time())



        if time % 20 == 0:
            print(f"{time}: Neuron 0 spikes ")
            neurons[0].emit_spike(time)


        if time % 20 == 4:
            print(f"{time}: Neuron 2 spikes ")
            neurons[2].emit_spike(time)

        #time = EDSynapse.event_manager.get_time()

        neuron_tracer.record(time)
        synapse_tracer.record(time)
        synapse_tracer2.record(time)

        time += 1



    print(f"Breaking because nb_events= {EDSynapse.event_manager.get_nb_events()} or {time} > MAX_TIME {MAX_TIME}")

    # print("NeuronTracer:")
    #
    # neuron_tracer.plot()
    #
    # print("synapseTracer:")
    #
    # synapse_tracer.plot()
    #
    # print("synapseTracer2:")
    #
    # synapse_tracer2.plot()
    #
    #


def test_three_input_neurons():


    EDSynapse.set_event_manager(EventManager())

    # Configuration
    neuron_config = NeuronConfig()
    neuron_config.THRESHOLD_REF = 1.0

    # Créer 3 neurones
    neurons = [EDNeuron(neuron_config) for _ in range(4)]
    print(f"Created {len(neurons)} neurons")

    # Connecter les neurones
    synapse_config = SynapseConfig()

    synapse_config.WEIGHT = 0.5  # Poids fort
    synapse_config.INITIAL_WEIGHT_MODE = "fixed"
    synapse_config.DELAY_MODE = "fixed"


    # N0 -> N1
    syn1 = EDSynapse(neurons[1], neurons[0], synapse_config)

    syn2 = EDSynapse(neurons[2], neurons[0], synapse_config)

    syn3 = EDSynapse(neurons[3], neurons[0], synapse_config)

    print("\nNetwork structure:")
    for neuron in neurons:
        print(f"  {neuron}: {len(neuron.incoming_links)} inputs, {len(neuron.outgoing_links)} outputs")


    # NeuronTracer
    neuron_tracer = NeuronTracer(neurons[0])
    neuron_tracer.record(0)

    # SynapseTracer
    synapse_tracer = SynapseTracer(syn1)
    synapse_tracer.record(0)

    synapse_tracer2 = SynapseTracer(syn2)
    synapse_tracer2.record(0)

    synapse_tracer3 = SynapseTracer(syn3)
    synapse_tracer3.record(0)


    # Simuler quelques impulsions
    print("\n--- Simulation ---")
    #
    #for i in range(10):
    #    neurons[0].emit_spike(i * 5)

    #     print(f"Init: Neuron 0 spikes: {i*10}")

    MAX_TIME = 200

    time = 0


    print(f"{time}: Neuron 0 spikes ")
    neurons[0].emit_spike(time)

    while time < MAX_TIME :

        print ("Queue: ", EDSynapse.event_manager.event_queue)
        print("Nb events: ", EDSynapse.event_manager.get_nb_events())

        if time == EDSynapse.event_manager.get_time():

            print("*** matching time: ", time)

            spike_neuron_ids = EDSynapse.event_manager.run_one_step()

            if len(spike_neuron_ids):
                print("Spike emissions by : ", spike_neuron_ids, " at time ", time)
        else:

            print("*** time: ", time, " != ", EDSynapse.event_manager.get_time())



        if time % 20 == 0:
            print(f"{time}: Neuron 1 spikes ")
            neurons[1].emit_spike(time)


        if time % 20 == 4:
            print(f"{time}: Neuron 2 spikes ")
            neurons[2].emit_spike(time)

        if time % 20 == 8:
            print(f"{time}: Neuron 3 spikes ")
            neurons[3].emit_spike(time)

        #time = EDSynapse.event_manager.get_time()

        neuron_tracer.record(time)

        synapse_tracer.record(time)
        synapse_tracer2.record(time)
        synapse_tracer3.record(time)

        time += 1



    print(f"Breaking because nb_events= {EDSynapse.event_manager.get_nb_events()} or {time} > MAX_TIME {MAX_TIME}")

    print("NeuronTracer:")

    neuron_tracer.plot()

    print("synapseTracer:")

    synapse_tracer.plot()

    print("synapseTracer2:")

    synapse_tracer2.plot()


    print("synapseTracer3:")

    synapse_tracer3.plot()





if __name__ == "__main__":
    #test_one_synapse()
    #test_two_input_neurons()
    test_three_input_neurons()
