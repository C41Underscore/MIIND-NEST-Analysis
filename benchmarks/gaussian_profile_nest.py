import matplotlib.pyplot as plt
import nest
from math import sqrt
from statistics import mean

NEST_VERSION = "nest-3.1"
try:
    NEST_VERSION = nest.__version__
except AttributeError:
    NEST_VERSION = "nest-2"

POPULATION_SIZE = 9500
SIMULATION_TIME = 500.

NUMBER_OF_DEVICES = 2


# print("h: " + str(H))
# print("v_in: " + str(V))


def write_gaussian_values():
    pass


def extract_spikes_from_recorder(filename, num_threads):
    spike_times = []
    for rank in range(0, num_threads):
        with open(filename % (POPULATION_SIZE + NUMBER_OF_DEVICES, rank)) as file:
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
individual_result = []

sigmas = [0.1, 0.3, 0.5, 0.7, 0.9]
for i in range(0, len(sigmas)):
    SIGMA = sigmas[i]
    MU = 0.1
    TAU = 50.
    current_results = []
    for j in range(0, 10):
        H = round((SIGMA ** 2) / MU, 3)
        nest.ResetKernel()
        nest.SetKernelStatus({"overwrite_files": True, "local_num_threads": 8})
        nest.set_verbosity(18)
        nest.SetDefaults("iaf_psc_delta", {"V_min": -1., "V_m": 0., "E_L": 0., "tau_m": TAU, "V_th": 1., "V_reset": 0.})

        pop = nest.Create("iaf_psc_delta", POPULATION_SIZE)

        if SIGMA < 0.5:
            NUMBER_OF_DEVICES = 2
            V = (MU ** 2) / ((TAU / 1000.) * (SIGMA ** 2))
            noise = nest.Create("poisson_generator")
            nest.SetStatus(noise, {"rate": V})
            nest.Connect(noise, pop, syn_spec={"weight": H})
        else:
            NUMBER_OF_DEVICES = 3
            J = 0.1
            V_E = round((J*MU + SIGMA**2)/(2*(TAU/1000.)*J**2), 3)
            V_I = round(((J*MU - SIGMA**2)/(2*(TAU/1000.)*J**2))*-1, 3)
            # print(SIGMA, MU, J, V_E, V_I)
            noise_ex = nest.Create("poisson_generator")
            noise_in = nest.Create("poisson_generator")
            nest.SetStatus(noise_ex, {"rate": V_E})
            nest.SetStatus(noise_in, {"rate": V_I})
            nest.Connect(noise_ex, pop, syn_spec={"weight": J})
            nest.Connect(noise_in, pop, syn_spec={"weight": -J})

        if NEST_VERSION == "nest-3.1":
            spike_recorder = nest.Create("spike_recorder", {"label": "gaussian", "record_to": "ascii"})
        else:
            spike_recorder = nest.Create("spike_detector")
            nest.SetStatus(spike_recorder, {"label": "gaussian", "record_to": ["file"]})
        nest.Connect(pop, spike_recorder)

        # print(nest.GetConnections())
        nest.Simulate(SIMULATION_TIME)

        spikes = extract_spikes_from_recorder(
                "gaussian-%s-%s.dat" if NEST_VERSION == "nest-3.1" else "gaussian-%s-%s.gdf",
                nest.GetKernelStatus("local_num_threads")
        )

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

        if SIGMA == 0.3 and MU == 0.7:
            individual_result = firing_rates.copy()

        current_results.append(mean(firing_rates))

        MU += 0.1
        if MU == 0:
            MU = 0.1
        MU = round(MU, 3)
    results.append(current_results)
    current_results = []

mus = [0.1 + i*0.1 for i in range(0, 10)]

with open("gaussians_nest.dat", "w") as file:
    file.write(",".join([str(i) for i in sigmas]) + "\n")
    file.write(",".join([str(round(i, 2)) for i in mus]) + "\n")
    for i in range(0, len(sigmas)):
        data = [str(round(i, 3)) for i in results[i]]
        data = ",".join(data) + "\n"
        file.write(data)

plt.figure(1)
plt.grid()
for i in range(0, len(sigmas)):
    plt.plot(mus, results[i], label="\u03C3: " + str(sigmas[i]))
plt.legend(loc="upper left")
plt.title("Gaussian Profile (NEST)")
# plt.figure(2)
# plt.grid()
# plt.plot(individual_result)

plt.show()
