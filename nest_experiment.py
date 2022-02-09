import matplotlib.pyplot as plt
import nest
from os.path import isdir
from os import mkdir, listdir
from shutil import rmtree
from time import perf_counter

# TODO: Plan and implement how data is written to file
# TODO: Work out how this simulation is going to be sped up to run large groups of neurons
# TODO: Implement the MIIND simulation
# TODO: Implement randomness into experiment

NEST_NEURON_MODEL = "iaf_cond_alpha"
NEST_SIMULATION_TIME = 200.

DATA_LOCATION = "nest_results/"
VOLTAGE_DATA_LOCATION = DATA_LOCATION + "multimeter/"
SPIKE_DATA_LOCATION = DATA_LOCATION + "spike_recorder/"

POPULATION_SIZES_MAX = 10
MAX_NUMBER_OF_CONNECTIONS = POPULATION_SIZES_MAX
NEST_SYNAPSE_TYPES = ["static_synapse", "tsodyks2_synapse"]


def extract_multimeter_data(filename):
    times = []
    voltage = []
    sim_size = 0
    file_parts = filename.split("_")
    sim_size = file_parts[1]
    with open(VOLTAGE_DATA_LOCATION + filename, "r") as file:
        file.readline()
        file.readline()
        file.readline()
        while file:
            line = file.readline().strip("\n")
            if line == "":
                break
            line = line.split('\t')
            times.append(str(line[1]))
            voltage.append(str(line[2]))
    return times, voltage


def compile_data():
    multimeter_files = listdir(VOLTAGE_DATA_LOCATION)
    spike_files = listdir(SPIKE_DATA_LOCATION)
    # extract self connected data
    self_connected_multimeter_files = []
    self_connected_spike_files = []
    for mf, sf in zip(multimeter_files, spike_files):
        if "selfconnected" == mf[0:13]:
            self_connected_multimeter_files.append(mf)
        if "selfconnected" == sf[0:13]:
            self_connected_spike_files.append(sf)
    self_connected_multimeter_data = []
    for file in self_connected_multimeter_files:
        data = extract_multimeter_data(file)


def kernel_settings():
    nest.set_verbosity(18)
    nest.SetKernelStatus({"overwrite_files": True})
    nest.SetDefaults(NEST_NEURON_MODEL, {"I_e": 0.})


def self_connected_network(size, connections, synapse_type, background_input):
    multimeter = nest.Create("multimeter")
    multimeter.set(record_to="ascii", record_from=["V_m"], label=str(VOLTAGE_DATA_LOCATION + "selfconnected_" + str(size) + "_"
                                                                     + str(connections) + "_" + str(synapse_type) + "_"
                                                                     + str(background_input)))

    spike_recorder = nest.Create("spike_recorder")
    spike_recorder.set(record_to="ascii", label=str(SPIKE_DATA_LOCATION + "selfconnected_" + str(size) + "_"
                                                                     + str(connections) + "_" + str(synapse_type) + "_"
                                                                     + str(background_input) + "_spikes"))

    pop = nest.Create(NEST_NEURON_MODEL, size)
    background_pop = nest.Create(NEST_NEURON_MODEL, size)
    background_pop.set({"I_e": 1000.})
    exc_poisson = nest.Create("poisson_generator")
    exc_poisson.set(rate=80000.)
    inh_poisson = nest.Create("poisson_generator")
    inh_poisson.set(rate=15000.)

    if background_input == "poisson":
        nest.Connect(exc_poisson, pop)
        nest.Connect(inh_poisson, pop)
    elif background_input == "cortical":
        pop.set({"I_e": 375.})
        # nest.Connect(background_pop, pop, {"rule": "all_to_all"},
        #         syn_spec={"synapse_model": synapse_type, "weight": 1., "delay": 1.})
        # nest.Connect(pop, pop, {"rule": "all_to_all"},
        #          syn_spec={"synapse_model": synapse_type, "weight": 2., "delay": 1.})

    nest.Connect(multimeter, pop)
    nest.Connect(pop, spike_recorder)


def balanced_ie_network(size, exc_connections, inh_connections, synapse_type, background_input):
    multimeter = nest.Create("multimeter")
    multimeter.set(record_to="ascii", record_from=["V_m"], label=str(VOLTAGE_DATA_LOCATION + "balancedIE_" + str(size) + "_" +
            str(exc_connections) + "_" + str(inh_connections) + "_" + str(synapse_type) + "_" + str(background_input)))

    spike_recorder = nest.Create("spike_recorder")
    spike_recorder.set(record_to="ascii", label=str(SPIKE_DATA_LOCATION + "balancedIE_" + str(size) + "_"
          + str(exc_connections) + "_" + str(inh_connections) + "_" + str(synapse_type) + "_" + str(background_input) +
                                                                         "_spikes"))

    # balanced I-E network
    epop = nest.Create(NEST_NEURON_MODEL, size)
    ipop = nest.Create(NEST_NEURON_MODEL, size)
    # background_pop = nest.Create("iaf_psc_alpha", size)
    # background_pop.set({"I_e": 1000.})
    exc_poisson = nest.Create("poisson_generator")
    exc_poisson.set(rate=80000.)
    inh_poisson = nest.Create("poisson_generator")
    inh_poisson.set(rate=15000.)

    if background_input == "cortical":
        epop.set({"I_e": 375.})
        ipop.set({"I_e": 375.})
        # nest.Connect(background_pop, epop, {"rule": "all_to_all"},
        #              syn_spec={"synapse_model": synapse_type, "weight": 1., "delay": 1.})
        # nest.Connect(background_pop, ipop, {"rule": "all_to_all"},
        #              syn_spec={"synapse_model": synapse_type, "weight": 1., "delay": 1.})
    elif background_input == "poisson":
        nest.Connect(exc_poisson, epop)
        nest.Connect(exc_poisson, ipop)
        nest.Connect(inh_poisson, epop)
        nest.Connect(inh_poisson, ipop)
    nest.Connect(epop, ipop, {"rule": "fixed_indegree", "indegree": exc_connections},
                 syn_spec={"synapse_model": synapse_type, "weight": 1., "delay": 1.})
    nest.Connect(ipop, epop, {"rule": "fixed_indegree", "indegree": inh_connections},
                 syn_spec={"synapse_model": synapse_type, "weight": -1., "delay": 1.})

    nest.Connect(multimeter, epop)
    nest.Connect(epop, spike_recorder)


def nest_experiment():
    count = 0
    print("---NEST EXPERIMENT START---")
    start = perf_counter()
    # Iterate over sizes
    for size in range(1, POPULATION_SIZES_MAX+1):
        for exc_connections in range(1, size+1):
            for inh_connections in range(1, size+1):
                # for synapse_type in NEST_SYNAPSE_TYPES:
                    for input_type in ["poisson", "cortical"]:
                        count += 1
                        kernel_settings()
                        balanced_ie_network(size, exc_connections, inh_connections, "static_synapse", input_type)
                        nest.Simulate(NEST_SIMULATION_TIME)
                        nest.ResetKernel()

    for size in range(1, POPULATION_SIZES_MAX+1):
        for connections in range(1, size+1):
            # for synapse_type in NEST_SYNAPSE_TYPES:
                for input_type in ["poisson", "cortical"]:
                    count += 1
                    kernel_settings()
                    self_connected_network(size, connections, "static_synapse", input_type)
                    nest.Simulate(NEST_SIMULATION_TIME)
                    nest.ResetKernel()

    total_time = round(perf_counter() - start, 2)
    print(str(count) + " experiments performed in " + str(total_time) + " seconds.")
    print("---NEST EXPERIMENT END---")


def nest_main():
    if isdir("nest_results/multimeter"):
        rmtree("nest_results/multimeter")
    mkdir("nest_results/multimeter")
    if isdir("nest_results/spike_recorder"):
        rmtree("nest_results/spike_recorder")
    mkdir("nest_results/spike_recorder")
    nest_experiment()
    # compile_data()


if __name__ == "__main__":
    nest_main()
