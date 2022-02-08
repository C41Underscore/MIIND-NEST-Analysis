import matplotlib.pyplot as plt
import nest
import miind.miindsim as miind

import nest_experiment

# Experiment ideas:
# - Change size of populations
# - Change connections within population e.g. synapse types, number etc.
# - Change inputs to these populations e.g. poisson inputs, background input etc.
# - Different types of simulation e.g. balanced inhibitory-exictatory networks, and self-connected networks etc.

POPULATION_SIZES_MAX = 1000
MAX_NUMBER_OF_CONNECTIONS = POPULATION_SIZES_MAX
NEST_SYNAPSE_TYPES = ["static_synapse_hom_w", "tsodyks2_synapse"]
OTHER_INPUT_TYPES = ["background_population"]
NEST_INPUT_TYPES = ["ac_generator", "dc_generator", "poisson_generator", OTHER_INPUT_TYPES]


def main():
    background_pop = nest.Create("iaf_psc_alpha", 100)
    background_pop.set({"I_e": 400.})
    epop = nest.Create("iaf_psc_alpha", 100)
    epop.set({"I_e": 376.})
    ipop = nest.Create("iaf_psc_alpha", 100)

    emm = nest.Create("voltmeter")
    imm = nest.Create("voltmeter")

    # nest.Connect(background_pop, epop, {"rule": "all_to_all"}, syn_spec={"weight": 1., "delay": 1.})
    nest.Connect(epop, epop, {"rule": "all_to_all"}, syn_spec={"weight": 1., "delay": 1.})
    # nest.Connect(ipop, epop, {"rule": "all_to_all"}, syn_spec={"weight": -1., "delay": 1.})
    # nest.Connect(epop, ipop, {"rule": "all_to_all"}, syn_spec={"weight": 1., "delay": 1.})

    nest.Connect(emm, epop)
    # nest.Connect(imm, ipop)

    nest.Simulate(1000.)

    dmm = emm.get()
    Vms = dmm["events"]["V_m"]
    ts = dmm["events"]["times"]

    plt.figure(1)
    plt.title("Excitatory Population")
    plt.plot(ts, Vms)

    # dmm = imm.get()
    # Vms = dmm["events"]["V_m"]
    # ts = dmm["events"]["times"]
    #
    # plt.figure(2)
    # plt.title("Inhibitory Population")
    # plt.plot(ts, Vms)

    plt.show()


if __name__ == "__main__":
    main()
