import matplotlib.pyplot as plt
import nest
import miind.miindsim as miind
from numpy.random import rand
from random import randint

import nest_experiment

# Experiment ideas:
# - Change size of populations
# - Change connections within population e.g. synapse types, number etc.
# - Change inputs to these populations e.g. poisson inputs, background input etc.
# - Different types of simulation e.g. balanced inhibitory-exictatory networks, and self-connected networks etc.

# TODO: Plan and implement how data is written to file
# TODO: Work out how this simulation is going to be sped up to run large groups of neurons
# TODO: Implement the MIIND simulation
# TODO: Implement randomness into experiment
# TODO: Add inhibitory spike recorder for nest


def p(t, dt, spikes, number_of_neurons):
    number_of_spikes = 0
    for i in range(0, len(spikes)):
        for j in range(0, len(spikes[i])):
            if t <= spikes[i][j] <= (t+dt):
                number_of_spikes += 1
    return (1/dt)*(number_of_spikes/number_of_neurons)


def main():
    Vrest = -70.
    Vth = -55.
    K = 5
    results = []
    for i in range(0, K):
        nest.set_verbosity(18)
        epop = nest.Create("iaf_cond_alpha", 1)
        epop.set({"I_e": 0., "V_reset": Vrest})

        exc_noise = nest.Create("poisson_generator")
        exc_noise.set(rate=15000.)

        emm = nest.Create("spike_recorder")
        nest.Connect(epop, epop, {"rule": "all_to_all"}, syn_spec={"weight": 1., "delay": 1.})
        nest.Connect(exc_noise, epop, syn_spec={"weight": 1., "delay": 1.})
        # nest.Connect(inh_noise, epop, syn_spec={"weight": -1., "delay": 1.})

        nest.Connect(epop, emm)

        nest.Simulate(500.)

        spikes = emm.get("events")["times"]
        results.append(spikes)
        nest.ResetKernel()

    for i in range(0, len(results)):
        for j in range(0, len(results[i])):
            results[i][j] /= 1000.
    print(results)
    # Rate as a Spike Count and Fano Factor
    # mean = sum(results)/len(results)
    # variance = [(results[i] - mean)**2 for i in range(0, len(results))]
    # variance_mean = sum(variance)/len(variance)
    # fano = variance_mean/mean

    # Rate as a Spike Density and the Peri-Stimulus-Time Histogram
    t = 0.
    step = 0.025
    times = []
    firing_rates = []
    while t < 0.5:
        times.append(str(t))
        firing_rates.append(p(t, step, results, 5))
        t += step
        t = round(t, 3)

    print(firing_rates)
    plt.figure(1)
    plt.title("Time-Dependent Firing Rate.")
    plt.bar(times, firing_rates)
    plt.show()


if __name__ == "__main__":
    main()
