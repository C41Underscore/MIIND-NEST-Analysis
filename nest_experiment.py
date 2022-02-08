import matplotlib.pyplot as plt
import nest
from os.path import isdir
from os import mkdir
from shutil import rmtree

# TODO: Implement data generation loop
    # TODO: Sort out issue where each experiment continues after the other i.e. membrane potential doesn't reset
# TODO: Plan and implement how data is written to file
# TODO: Implement randomness into experiment

DATA_LOCATION = "nest_results/"

POPULATION_SIZES_MAX = 10
MAX_NUMBER_OF_CONNECTIONS = POPULATION_SIZES_MAX
NEST_SYNAPSE_TYPES = ["static_synapse", "tsodyks2_synapse"]
# CONNECTION_RULES = [(False, False), (False, True), (True, False), (True, True)]  # Autapses, Multapses


def self_connected_network(size, connections, synapse_type, background_input):
    multimeter = nest.Create("multimeter")
    multimeter.set(record_to="ascii", record_from=["V_m"], label=str(DATA_LOCATION + "selfconnected_" + str(size) + "_"
                                                                     + str(connections) + "_" + str(synapse_type) + "_"
                                                                     + str(background_input)))

    spike_recorder = nest.Create("spike_recorder")
    spike_recorder.set(record_to="ascii", label=str(DATA_LOCATION + "selfconnected_" + str(size) + "_"
                                                                     + str(connections) + "_" + str(synapse_type) + "_"
                                                                     + str(background_input) + "_spikes"))

    pop = nest.Create("iaf_psc_alpha", size)
    background_pop = nest.Create("iaf_psc_alpha", size)
    background_pop.set({"I_e": 376.})

    nest.Connect(background_pop, pop, {"rule": "all_to_all"},
                 syn_spec={"synapse_model": synapse_type, "weight": 1., "delay": 1.})
    nest.Connect(pop, pop, {"rule": "all_to_all"},
                 syn_spec={"synapse_model": synapse_type, "weight": 2., "delay": 1.})

    nest.Connect(multimeter, pop)
    nest.Connect(pop, spike_recorder)


def balanced_ie_network(size, exc_connections, inh_connections, synapse_type, background_input):
    multimeter = nest.Create("multimeter")
    multimeter.set(record_to="ascii", record_from=["V_m"], label=str(DATA_LOCATION + "balancedIE_" + str(size) + "_" +
            str(exc_connections) + "_" + str(inh_connections) + "_" + str(synapse_type) + "_" + str(background_input)))

    spike_recorder = nest.Create("spike_recorder")
    spike_recorder.set(record_to="ascii", label=str(DATA_LOCATION + "balancedIE_" + str(size) + "_"
          + str(exc_connections) + "_" + str(inh_connections) + "_" + str(synapse_type) + "_" + str(background_input) +
                                                                         "_spikes"))

    # balanced E-I network
    background_pop = nest.Create("iaf_psc_alpha", size)
    background_pop.set({"I_e": 376.})
    epop = nest.Create("iaf_psc_alpha", size)
    ipop = nest.Create("iaf_psc_alpha", size)

    nest.Connect(background_pop, epop, {"rule": "all_to_all"},
                 syn_spec={"synapse_model": synapse_type, "weight": 1., "delay": 1.})
    nest.Connect(background_pop, ipop, {"rule": "all_to_all"},
                 syn_spec={"synapse_model": synapse_type, "weight": 1., "delay": 1.})
    nest.Connect(epop, ipop, {"rule": "fixed_indegree", "indegree": exc_connections},
                 syn_spec={"synapse_model": synapse_type, "weight": 1., "delay": 1.})
    nest.Connect(ipop, epop, {"rule": "fixed_indegree", "indegree": inh_connections},
                 syn_spec={"synapse_model": synapse_type, "weight": -1., "delay": 1.})

    nest.Connect(multimeter, epop)
    nest.Connect(background_pop, epop)


def nest_experiment():
    count = 0
    print("---NEST EXPERIMENT START---")
    # Iterate over sizes
    for size in range(1, POPULATION_SIZES_MAX+1):
        for exc_connections in range(1, size+1):
            for inh_connections in range(1, size+1):
                for synapse_type in NEST_SYNAPSE_TYPES:
                    count += 1

                    nest.set_verbosity(18)
                    nest.SetKernelStatus({"overwrite_files": True})
                    nest.SetDefaults("iaf_psc_alpha", {"I_e": 0., "tau_m": 20.})

                    balanced_ie_network(size, exc_connections, inh_connections, synapse_type, "cortical")
                    nest.Simulate(1000.)
                    nest.ResetKernel()

    for size in range(1, POPULATION_SIZES_MAX+1):
        for connections in range(1, size+1):
            for synapse_type in NEST_SYNAPSE_TYPES:
                count += 1

                nest.set_verbosity(18)
                nest.SetKernelStatus({"overwrite_files": True})
                nest.SetDefaults("iaf_psc_alpha", {"I_e": 0., "tau_m": 20.})

                self_connected_network(size, connections, synapse_type, "cortical")
                nest.Simulate(1000.)
                nest.ResetKernel()

    print("Number of Experiments: " + str(count))
    print("---NEST EXPERIMENT END---")


def nest_main():
    if isdir("nest_results"):
        rmtree("nest_results")
    mkdir("nest_results")
    nest_experiment()


if __name__ == "__main__":
    nest_main()
