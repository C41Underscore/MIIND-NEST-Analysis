import matplotlib.pyplot as plt
import miind.miindsim as miind
import nest

# Experiment ideas:
# - Change size of populations
# - Change connections within population e.g. synapse types, number etc.
# - Change inputs to these populations e.g. poisson inputs, background input etc.
# - Different types of simulation e.g. balanced inhibitory-exictatory networks, and self-connected networks etc.

POPULATION_SIZES_MAX = 1000


def nest_experiment():
    ex_pop = nest.Create("iaf_psc_alpha", POPULATION_SIZES_MAX, params={"I_e": 0., "tau_m": 20.})
    in_pop = nest.Create("iaf_psc_alpha", POPULATION_SIZES_MAX, params={"I_e": 0., "tau_m": 20.})
    background_pop = nest.Create("iaf_psc_alpha", POPULATION_SIZES_MAX, params={"I_e": 375., "tau_m": 20.})

    nest.Connect(background_pop, ex_pop, {"rule": "all_to_all"}, {"weight": 1., "delay": 1.})
    nest.Connect(background_pop, in_pop, {"rule": "all_to_all"}, {"weight": 1., "delay": 1.})
    nest.Connect(ex_pop, in_pop, {"rule": "all_to_all"}, {"weight": 1., "delay": 1.})
    nest.Connect(in_pop, ex_pop, {"rule": "all_to_all"}, {"weight": -1., "delay": 1.})

    ex_multimeter = nest.Create("multimeter", params={"label": "Excitatory"})
    ex_multimeter.set(record_from=["V_m"])
    nest.Connect(ex_multimeter, ex_pop)

    in_multimeter = nest.Create("multimeter", params={"label": "Inhibitory"})
    in_multimeter.set(record_from=["V_m"])
    nest.Connect(in_multimeter, in_pop)

    nest.Simulate(1000.)

    dmm = ex_multimeter.get()
    vms = dmm["events"]["V_m"]
    ts = dmm["events"]["times"]
    plt.figure(1)
    plt.title("Excitatory")
    plt.plot(ts, vms)

    dmm = in_multimeter.get()
    vms = dmm["events"]["V_m"]
    ts = dmm["events"]["times"]
    plt.title("Inhibitory")
    plt.figure(2)
    plt.plot(ts, vms)

    plt.show()


def main():
    nest_experiment()


if __name__ == "__main__":
    main()
