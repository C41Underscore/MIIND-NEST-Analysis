import matplotlib.pyplot as plt
from scipy.interpolate import make_interp_spline, BSpline
from numpy import linspace
from time import perf_counter
from os import environ
import nest

NEST_VERSION = "nest-3.1"
try:
    NEST_VERSION = nest.__version__
except AttributeError:
    NEST_VERSION = "nest-2"

POPULATION_SIZE = 950
SIMULATION_TIME = 200.
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
if NEST_VERSION == "nest-3.1":
    nest.ResetKernel()
else:
    nest.ResetNetwork()
nest.SetKernelStatus({"overwrite_files": True, "local_num_threads": NUMBER_OF_THREADS})

n_dict = {"V_reset": 0., "tau_m": 50., "V_th": 1., "E_L": 0., "V_m": 0.}
nest.SetDefaults("iaf_psc_delta", n_dict)
nest.SetDefaults("poisson_generator", {"rate": 800.})

pop = nest.Create("iaf_psc_delta", POPULATION_SIZE)
noise = nest.Create("poisson_generator")
spike_recorder = nest.Create("spike_recorder" if NEST_VERSION == "nest-3.1" else "spike_detector")
if NEST_VERSION == "nest-3.1":
    nest.SetStatus(spike_recorder, {"record_to": "ascii", "label": "omurtag"})
else:
    nest.SetStatus(spike_recorder, {"record_to": ["file"], "label": "omurtag"})

nest.Connect(noise, pop, syn_spec={"weight": 0.03, "delay": 1.})
nest.Connect(pop, spike_recorder)

nest.Simulate(SIMULATION_TIME)

spikes = extract_spikes_from_recorder("omurtag-%s-%s.dat" if NEST_VERSION == "nest-3.1" else "omurtag-%s-%s.gdf",
                                      nest.GetKernelStatus("local_num_threads"))

t = 0.
dt = 10.
firing_rates = []
while t < SIMULATION_TIME:
    count = 0
    for i in range(0, len(spikes)):
        if t < spikes[i] < t+dt:
            count += 1
    count = (1000./dt)*(count/POPULATION_SIZE)
    firing_rates.append(str(round(count, 3)))
    t += dt


data_string = ",".join(firing_rates)
with open("omurtag.dat", "w") as data_file:
    data_file.write(data_string)


sim_end = perf_counter() - sim_start

print("\nSimulation and Analysis time: " + str(sim_end))
