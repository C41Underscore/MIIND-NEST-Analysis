import matplotlib.pyplot as plt
import nest
from os.path import isdir
from os import mkdir, listdir, chdir, getcwd
from shutil import rmtree
from time import perf_counter
from random import uniform


NEST_NEURON_MODEL = "iaf_cond_alpha"
NEST_SIMULATION_TIME = 200.

DATA_LOCATION = "nest_results/"
VOLTAGE_DATA_LOCATION = DATA_LOCATION + "multimeter/"
SPIKE_DATA_LOCATION = DATA_LOCATION + "spike_recorder/"
ANALYSIS_TIME_STEP = 0.01
NUMBER_OF_REPEATS = 5

POPULATION_SIZE_MIN = 5
POPULATION_SIZE_MAX = 5
MAX_NUMBER_OF_CONNECTIONS = POPULATION_SIZE_MAX
NEST_SYNAPSE_TYPES = ["static_synapse", "tsodyks2_synapse"]


def create_and_reset_sim_dir(name):
    if isdir(name):
        rmtree(name)
    mkdir(name)


# Rate as a Population Activity (Average over Several Neurons, Average over Several Runs)
def average_firing_rate(t, dt, spikes):
    average_rate = 0
    for i in range(0, len(spikes)):
        number_of_spikes = 0
        for j in range(0, len(spikes[i])):
            if t <= spikes[i][j] <= (t+dt):
                number_of_spikes += 1
        average_rate += (1/len(spikes))*(1/dt)*(number_of_spikes/POPULATION_SIZE_MAX)
    return round(average_rate, 5)


def extract_spikes_from_recorder(filename):
    spike_times = []
    with open(filename) as file:
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


def extract_multimeter_data(filename):
    times = []
    voltage = []
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


def record_spikes(filename, firing_rates):
    with open(filename + ".dat", "w") as file:
        data = str(firing_rates)
        data = data[1:len(data) - 2]
        file.write(data)


def analyse_firing_rates(files):
    spikes = []
    for file in files:
        spikes.append([spike / 1000. for spike in extract_spikes_from_recorder(file)])
    firing_rates = []
    t = 0.
    while t < NEST_SIMULATION_TIME / 1000.:
        firing_rates.append(average_firing_rate(t, ANALYSIS_TIME_STEP, spikes))
        t += ANALYSIS_TIME_STEP
    return firing_rates


def compile_data():
    spike_files = listdir("./")
    # extract self connected data
    balanced_ie_spike_files = []
    self_connected_spike_files = []
    for sf in spike_files:
        if "balancedIE" == sf[0:10]:
            balanced_ie_spike_files.append(sf)
        else:
            self_connected_spike_files.append(sf)
    for sim_dir in balanced_ie_spike_files:
        chdir(sim_dir)
        exc_files = []
        inh_files = []
        files = listdir("./")
        for file in files:
            if file[0:3] == "exc":
                exc_files.append(file)
            else:
                inh_files.append(file)
        exc_firing_rates = analyse_firing_rates(exc_files)
        record_spikes("exc_firing_rates", exc_firing_rates)
        inh_firing_rates = analyse_firing_rates(inh_files)
        record_spikes("inh_firing_rate", inh_firing_rates)
        chdir("..")
    for sim_dir in self_connected_spike_files:
        # print(sim_dir)
        chdir(sim_dir)
        files = listdir("./")
        firing_rates = analyse_firing_rates(files)
        record_spikes("firing_rates", firing_rates)
        chdir("..")


def kernel_settings():
    nest.set_verbosity(18)
    nest.SetKernelStatus({"overwrite_files": True})
    nest.SetDefaults(NEST_NEURON_MODEL, {"I_e": 0.})
    nest.rng_seed = int(uniform(0., 2**32-1))


def self_connected_network(size, connections, background_input, experiment_number):
    spike_recorder = nest.Create("spike_recorder")
    spike_recorder.set(record_to="ascii", label=str("test" + str(experiment_number)))
    pop = nest.Create(NEST_NEURON_MODEL, size)
    exc_poisson = nest.Create("poisson_generator")
    exc_poisson.set(rate=8000.)
    inh_poisson = nest.Create("poisson_generator")
    inh_poisson.set(rate=1500.)

    if background_input == "poisson":
        nest.Connect(exc_poisson, pop, syn_spec={"weight": 1.})
        nest.Connect(inh_poisson, pop, syn_spec={"weight": -1.})
    elif background_input == "cortical":
        pop.set({"I_e": nest.random.uniform(min=376., max=450.)})

    # nest.Connect(pop, pop, {"rule": "fixed_indegree", "indegree": connections},
    #              syn_spec={"weight": 1.,
    #                        "delay": 1.})
    nest.Connect(pop, pop, {"rule": "fixed_indegree", "indegree": connections},
                 syn_spec={"weight": nest.random.uniform(min=0., max=2.),
                           "delay": 1.})

    nest.Connect(pop, spike_recorder)


def balanced_ie_network(size, exc_connections, inh_connections, background_input, experiment_number):
    exc_spike_recorder = nest.Create("spike_recorder")
    exc_spike_recorder.set(record_to="ascii", label=str("exc_test" + str(experiment_number)))

    inh_spike_recorder = nest.Create("spike_recorder")
    inh_spike_recorder.set(record_to="ascii", label=str("inh_test" + str(experiment_number)))

    # balanced I-E network
    epop = nest.Create(NEST_NEURON_MODEL, size)
    ipop = nest.Create(NEST_NEURON_MODEL, size)
    exc_poisson = nest.Create("poisson_generator")
    exc_poisson.set(rate=8000.)
    inh_poisson = nest.Create("poisson_generator")
    inh_poisson.set(rate=1500.)

    if background_input == "cortical":
        epop.set({"I_e": 376.})
        ipop.set({"I_e": 376.})
    elif background_input == "poisson":
        nest.Connect(exc_poisson, epop, syn_spec={"weight": 1.})
        nest.Connect(exc_poisson, ipop, syn_spec={"weight": -1.})
        nest.Connect(inh_poisson, epop, syn_spec={"weight": 1.})
        nest.Connect(inh_poisson, ipop, syn_spec={"weight": -1.})
    nest.Connect(epop, epop, {"rule": "fixed_indegree", "indegree": exc_connections},
                 syn_spec={"weight": nest.random.uniform(min=0., max=2.),
                           "delay": 1.})
    nest.Connect(ipop, ipop, {"rule": "fixed_indegree", "indegree": inh_connections},
                 syn_spec={"weight": nest.random.uniform(min=-2., max=0.),
                           "delay": 1.})
    nest.Connect(epop, ipop, {"rule": "fixed_indegree", "indegree": exc_connections},
                 syn_spec={"weight": nest.random.uniform(min=0., max=2.),
                           "delay": 1.})
    nest.Connect(ipop, epop, {"rule": "fixed_indegree", "indegree": inh_connections},
                 syn_spec={"weight": nest.random.uniform(min=-2., max=0.),
                           "delay": 1.})

    nest.Connect(epop, exc_spike_recorder)
    nest.Connect(ipop, inh_spike_recorder)


def nest_experiment():
    count = 0
    print("---NEST EXPERIMENT START---")
    start = perf_counter()
    # Iterate over sizes
    # for size in range(1, POPULATION_SIZE_MAX + 1):
    for exc_connections in range(1, POPULATION_SIZE_MAX+1):
        for inh_connections in range(1, POPULATION_SIZE_MAX+1):
            for input_type in ["poisson", "cortical"]:
                sim_name = "balancedIE_" + str(exc_connections) + "_" + \
                           str(inh_connections) + "_" + str(input_type)
                create_and_reset_sim_dir(sim_name)
                chdir(sim_name)
                for i in range(1, NUMBER_OF_REPEATS+1):
                    count += 1
                    kernel_settings()
                    balanced_ie_network(POPULATION_SIZE_MAX, exc_connections, inh_connections, input_type, i)
                    nest.Simulate(NEST_SIMULATION_TIME)
                    nest.ResetKernel()
                chdir("..")

    for connections in range(1, POPULATION_SIZE_MAX+1):
        for input_type in ["poisson", "cortical"]:
            sim_name = "selfconnected_" + str(connections) + "_" + str(input_type)
            create_and_reset_sim_dir(sim_name)
            chdir(sim_name)
            for i in range(0, NUMBER_OF_REPEATS):
                count += 1
                kernel_settings()
                self_connected_network(POPULATION_SIZE_MAX, connections, input_type, i)
                nest.Simulate(NEST_SIMULATION_TIME)
                nest.ResetKernel()
            chdir("..")

    total_time = round(perf_counter() - start, 2)
    print(str(count) + " experiments performed in " + str(total_time) + " seconds.")
    print("---NEST EXPERIMENT END---")


def main():
    if isdir("nest_results"):
        rmtree("nest_results")
    mkdir("nest_results")
    chdir("nest_results")
    nest_experiment()
    compile_data()


def run_nest_experiment():
    main()


if __name__ == "__main__":
    main()
