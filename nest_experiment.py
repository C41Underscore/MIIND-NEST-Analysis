import matplotlib.pyplot as plt
import nest
from os import remove

# TODO: Implement data generation loop
    # TODO: Sort out issue where each experiment continues after the other i.e. membrane potential doesn't reset
# TODO: Plan and implement how data is written to file
# TODO: Implement randomness into experiment

POPULATION_SIZES_MAX = 1
MAX_NUMBER_OF_CONNECTIONS = POPULATION_SIZES_MAX
NEST_SYNAPSE_TYPES = ["tsodyks2_synapse", "static_synapse_hom_w"]
CONNECTION_RULES = [(False, False), (False, True), (True, False), (True, True)]  # Autapses, Multapses


NEST_MULTIMETER = nest.Create("multimeter")
NEST_SPIKE_RECORDER = nest.Create("spike_recorder")


def run_nest_experiment(size, connections, type, rule):
    pass


def nest_experiment():
    nest.set_verbosity(18)
    nest.SetKernelStatus({"overwrite_files": True})
    nest.SetDefaults("iaf_psc_alpha", {"I_e": 0., "tau_m": 20.})

    NEST_MULTIMETER.set(record_to="ascii", label="test1", record_from=["V_m"])

    # balanced E-I network
    background_pop = nest.Create("iaf_psc_alpha", 1)
    background_pop.set({"I_e": 500.})
    epop = nest.Create("iaf_psc_alpha", 1)
    ipop = nest.Create("iaf_psc_alpha", 1)

    nest.Connect(background_pop, epop, {"rule": "all_to_all"}, syn_spec={"weight": 1., "delay": 1.})
    nest.Connect(background_pop, ipop, {"rule": "all_to_all"}, syn_spec={"weight": 1., "delay": 1.})
    nest.Connect(epop, ipop, {"rule": "all_to_all"}, syn_spec={"weight": 1., "delay": 1.})
    nest.Connect(ipop, epop, {"rule": "all_to_all"}, syn_spec={"weight": -1., "delay": 1.})

    nest.Connect(NEST_MULTIMETER, epop)

    # self-connected excitatory network

    conns = nest.GetConnections()
    # print(conns)

    print("Number of Connections: " + str(nest.num_connections))

    count = 0
    # Iterate over sizes
    for size in range(1, POPULATION_SIZES_MAX+1):
        for synapse_type in NEST_SYNAPSE_TYPES:
            count += 1

            print(epop.get("V_m"), ipop.get("V_m"), background_pop.get("V_m"))

            conns = nest.GetConnections()
            conns.model = synapse_type

            background_pop.set({"I_e": 376.})

            NEST_MULTIMETER.set({"label": synapse_type + str(count)})

            nest.Simulate(25.)

            background_pop.set({"I_e": 0.})
            NEST_MULTIMETER.set({"label": "aux" + str(count)})
            nest.Simulate(100.)

                    # print("Test {0} - Size {1} - Connections {2} - Synapse Type {3} - Autapses {4} - Multapses {5}"
                    #       .format(count, size, connections, type, rule[0], rule[1]))
                # Compute for background population
                    # Compute for balanced I-E
                    # nest.Simulate(1000.)

                    # Compute for self connected E/I
                # Compute for poisson
                    # Compute for balanced I-E
                    # Compute for self connected E/I
    print("Number of Experiments: " + str(count))


def main():
    global NEST_MULTIMETER
    NEST_MULTIMETER.set(record_to="ascii", label="test1", record_from=["V_m"])
    nest_experiment()


if __name__ == "__main__":
    main()
