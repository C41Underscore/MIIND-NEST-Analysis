import matplotlib.pyplot as plt
from scipy.interpolate import make_interp_spline, BSpline
from numpy import linspace
from time import perf_counter
import nest


POPULATION_SIZE = 95000
SIMULATION_TIME = 1000
NUMBER_OF_THREADS = 8


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


sim_start = perf_counter()
nest.ResetKernel()
nest.overwrite_files = True
# nest.total_num_virtual_procs = 4
nest.local_num_threads = NUMBER_OF_THREADS

n_dict = {"V_reset": 0., "tau_m": 50., "V_th": 1., "E_L": 0., "V_m": 0.}
nest.SetDefaults("iaf_psc_delta", n_dict)

pop = nest.Create("iaf_psc_delta", POPULATION_SIZE)
input = nest.Create("poisson_generator", {"rate": 800.})
spike_recorder = nest.Create("spike_recorder", {"label": "omurtag", "record_to": "ascii"})

nest.Connect(input, pop, syn_spec={"weight": 0.03, "delay": 1.})
nest.Connect(pop, spike_recorder)

nest.Simulate(SIMULATION_TIME)

spikes = extract_spikes_from_recorder("omurtag-%s-%s.dat", NUMBER_OF_THREADS)

t = 0.
dt = 10.
firing_rates = []
while t < SIMULATION_TIME:
    count = 0
    for i in range(0, len(spikes)):
        if t < spikes[i] < t+dt:
            count += 1
    count = (1000./dt)*(count/POPULATION_SIZE)
    firing_rates.append(count)
    t += dt

sim_end = perf_counter() - sim_start

print("\nSimulation and Analysis time: " + str(sim_end))

times = [i for i in range(0, SIMULATION_TIME, int(dt))]


# average_firing_rates = []
# for i in range(0, len(results[0])):
#     average = sum([results[j][i] for j in range(0, len(results))])/len(results)
#     average_firing_rates.append(average)


# Curve smoothing tings
smoothed_times = linspace(min(times), max(times), SIMULATION_TIME)
spl = make_interp_spline(times, firing_rates, k=3)
smoothed_rates = spl(smoothed_times)

plt.figure(1)
plt.title("Firing Rate.")
plt.plot(smoothed_times, smoothed_rates)
plt.show()
