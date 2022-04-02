import matplotlib.pyplot as plt
import nest
from math import sqrt
from statistics import mean

POPULATION_SIZE = 950
SIMULATION_TIME = 1000.


# print("h: " + str(H))
# print("v_in: " + str(V))


def write_gaussian_values():
    pass


def extract_spikes_from_recorder(filename, num_threads):
    spike_times = []
    for rank in range(0, num_threads):
        with open(filename % (POPULATION_SIZE + 2, rank)) as file:
            file.readline()
            file.readline()
            file.readline()
            while file:
                line = file.readline().strip("\n")
                if line == "":
                    break
                line = line.split("\t")
                spike_times.append(float(line[1]))
    return spike_times


results = []
# mus = [MU + i*0.1 for i in range(0, 6)]

sigmas = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
for i in range(0, len(sigmas)):
    SIGMA = sigmas[i]
    MU = 0.1
    TAU = 10.
    current_results = []
    for j in range(0, 6):
        H = (SIGMA ** 2) / MU
        V = (MU ** 2) / ((TAU / 1000.) * (SIGMA ** 2))
        nest.ResetKernel()
        nest.local_num_threads = 8
        nest.overwrite_files = True
        nest.set_verbosity(18)

        nest.SetDefaults("iaf_psc_delta", {"V_m": 0., "E_L": 0., "tau_m": TAU, "V_th": 1., "V_reset": 0.})

        pop = nest.Create("iaf_psc_delta", POPULATION_SIZE)
        noise = nest.Create("poisson_generator")
        noise.set(rate=V)
        spike_recorder = nest.Create("spike_recorder", {"label": "gaussian", "record_to": "ascii"})

        nest.Connect(noise, pop, syn_spec={"weight": H})
        nest.Connect(pop, spike_recorder)

        nest.Simulate(1000.)

        spikes = extract_spikes_from_recorder("gaussian-%s-%s.dat", nest.local_num_threads)

        t = 0.
        dt = 10.
        firing_rates = []
        while t < SIMULATION_TIME:
            count = 0
            for x in range(0, len(spikes)):
                if t < spikes[x] < t+dt:
                    count += 1
            count = (1000./dt)*(count/POPULATION_SIZE)
            firing_rates.append(count)
            t += dt

        current_results.append(mean(firing_rates))

        MU += 0.1
        if MU == 0:
            MU = 0.1
        MU = round(MU, 3)
    results.append(current_results)
    current_results = []

parameter_results = []
tau = 0.01
for j in range(0, 20):
    sigma = 1.0
    mu = 0.1 + j/10.
    h = sigma**2 / mu
    v = mu**2 / tau*sigma**2
    parameter_results.append((round(v, 3), round(h, 3)))

print(parameter_results)
v_values = [i[0] for i in parameter_results]
h_values = [i[1] for i in parameter_results]

x = [0.1 + i*0.1 for i in range(0, 6)]
# print(x)

plt.figure(1)
plt.grid()
for i in range(0, len(sigmas)):
    plt.plot(x, results[i], label="\u03C3: " + str(sigmas[i]))
plt.legend(loc="upper left")

plt.figure(2)
plt.grid()
plt.plot(v_values, h_values)

plt.show()