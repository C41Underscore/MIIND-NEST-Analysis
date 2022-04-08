import nest
from os.path import isdir
from os import mkdir, listdir, chdir, getcwd
from shutil import rmtree
from time import perf_counter
from random import uniform


NEST_NEURON_MODEL = "iaf_psc_delta"
NEST_SIMULATION_TIME = 1000.
NEST_NUMBER_OF_THREADS = 8
NEST_VERSION = "nest-3.1"
pyrngs = []
try:
    NEST_VERSION = nest.__version__
except AttributeError:
    NEST_VERSION = "nest-2.2"

if NEST_VERSION == "nest-2.2":
    import numpy as np

DATA_LOCATION = "nest_results/"
SPIKE_DATA_LOCATION = DATA_LOCATION + "spike_recorder/"
ANALYSIS_TIME_STEP = 0.01
NUMBER_OF_REPEATS = 5

POPULATION_SIZE = 10


def create_and_reset_sim_dir(name):
    if isdir(name):
        rmtree(name)
    mkdir(name)


# Rate as a Population Activity (Average over Several Neurons, Average over Several Runs)
def average_firing_rate(t, dt, spikes):
    # average_rate = []
    average_rate = 0
    for i in range(0, len(spikes)):
        number_of_spikes = 0
        for j in range(0, len(spikes[i])):
            if t <= spikes[i][j] <= (t+dt):
                number_of_spikes += 1
        average_rate += (1/len(spikes))*(1/dt)*(number_of_spikes / POPULATION_SIZE)
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


def record_spikes(filename, firing_rates):
    with open(filename + ".dat", "w") as file:
        data = str(firing_rates)
        data = data[1:len(data) - 2]
        file.write(data)


def analyse_firing_rates(files):
    spikes = []
    for file in files:
        spikes.append([spike / 1000. for spike in
                       extract_spikes_from_recorder(file)])
    firing_rates = []
    t = 0.
    while t < NEST_SIMULATION_TIME / 1000.:
        firing_rates.append(average_firing_rate(t, ANALYSIS_TIME_STEP, spikes))
        t += ANALYSIS_TIME_STEP
    return firing_rates


def compile_data():
    spike_files = listdir("./")
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
        chdir(sim_dir)
        files = listdir("./")
        firing_rates = analyse_firing_rates(files)
        record_spikes("firing_rates", firing_rates)
        chdir("..")


def kernel_settings():
    global pyrngs
    nest.set_verbosity(18)
    nest.SetKernelStatus(
        {
            "local_num_threads": NEST_NUMBER_OF_THREADS,
            "overwrite_files": True
        }
    )
    if NEST_VERSION == "nest-3.1":
        nest.rng_seed = int(uniform(0., 2**32 - 1))
    else:
        # code from: https://nest-simulator.org/wp-content/uploads/2015/02/NEST_by_Example.pdf, page 12
        msd = int(uniform(0., 2**32 - 1))
        n_vp = nest.GetKernelStatus("total_num_virtual_procs")
        msdrange1 = range(msd, msd+n_vp)
        pyrngs = [np.random.RandomState(s) for s in msdrange1]
        msdrange2 = range(msd+n_vp+1, msd+1+2*n_vp)
        nest.SetKernelStatus({"grng_seed": msd+n_vp, "rng_seeds": msdrange2})
    nest.SetDefaults(NEST_NEURON_MODEL, {"I_e": 0., "V_th": -55., "V_reset": -70., "E_L": -70., "tau_m": 50.})


def self_connected_network(size, connections, experiment_number):
    if NEST_VERSION == "nest-3.1":
        spike_recorder = nest.Create("spike_recorder")
        spike_recorder.set(record_to="ascii", label=str("test" + str(experiment_number)))
    else:
        spike_recorder = nest.Create("spike_detector")
        nest.SetStatus(spike_recorder, {
            "record_to": ["file"], "label": str("test" + str(experiment_number)), "file_extension": "dat"
        })
    pop = nest.Create(NEST_NEURON_MODEL, size)

    exc_poisson = nest.Create("poisson_generator")
    inh_poisson = nest.Create("poisson_generator")
    if NEST_VERSION == "nest-3.1":
        exc_poisson.set(rate=80000.)
        inh_poisson.set(rate=15000.)
    else:
        nest.SetStatus(exc_poisson, {"rate": 80000})
        nest.SetStatus(inh_poisson, {"rate": 15000})

    nest.Connect(exc_poisson, pop, syn_spec={"weight": 1.})
    nest.Connect(inh_poisson, pop, syn_spec={"weight": -1.})

    if NEST_VERSION == "nest-3.1":
        nest.Connect(pop, pop, {"rule": "fixed_indegree", "indegree": connections},
                    syn_spec={"weight": nest.random.uniform(min=0., max=2.),
                            "delay": 1.})
    else:
        nest.Connect(pop, pop, {"rule": "fixed_indegree", "indegree": connections},
                     syn_spec={"model": "excitatory",
                               "weight": {"distribution": "uniform", "low": 0., "high": 1.},
                               "delay": 1.})

    nest.Connect(pop, spike_recorder)


def balanced_ie_network(size, exc_connections, inh_connections, experiment_number):
    if NEST_VERSION == "nest-3.1":
        exc_spike_recorder = nest.Create("spike_recorder")
        exc_spike_recorder.set(record_to="ascii", label=str("exc_test" + str(experiment_number)))
        inh_spike_recorder = nest.Create("spike_recorder")
        inh_spike_recorder.set(record_to="ascii", label=str("inh_test" + str(experiment_number)))
    else:
        exc_spike_recorder = nest.Create("spike_detector")
        nest.SetStatus(exc_spike_recorder, {
            "record_to": ["file"], "label": str("exc_test" + str(experiment_number)), "file_extension": "dat"
        })
        inh_spike_recorder = nest.Create("spike_detector")
        nest.SetStatus(inh_spike_recorder, {
            "record_to": ["file"], "label": str("inh_test" + str(experiment_number)), "file_extension": "dat"
        })

    # balanced I-E network
    epop = nest.Create(NEST_NEURON_MODEL, size)
    ipop = nest.Create(NEST_NEURON_MODEL, size)
    exc_poisson = nest.Create("poisson_generator")
    inh_poisson = nest.Create("poisson_generator")
    if NEST_VERSION == "nest-3.1":
        exc_poisson.set(rate=80000.)
        inh_poisson.set(rate=15000.)
    else:
        nest.SetStatus(exc_poisson, {"rate": 80000.})
        nest.SetStatus(inh_poisson, {"rate": 15000.})

    nest.Connect(exc_poisson, epop, syn_spec={"weight": 1.})
    nest.Connect(exc_poisson, ipop, syn_spec={"weight": 1.})
    nest.Connect(inh_poisson, epop, syn_spec={"weight": -1.})
    nest.Connect(inh_poisson, ipop, syn_spec={"weight": -1.})

    if NEST_VERSION == "nest-3.1":
        nest.Connect(epop, epop, {"rule": "fixed_indegree", "indegree": exc_connections},
                     syn_spec={"weight": nest.random.uniform(min=0., max=1.),
                               "delay": 1.})
        nest.Connect(ipop, ipop, {"rule": "fixed_indegree", "indegree": inh_connections},
                     syn_spec={"weight": nest.random.uniform(min=-1., max=0.),
                               "delay": 1.})
        nest.Connect(epop, ipop, {"rule": "fixed_indegree", "indegree": exc_connections},
                     syn_spec={"weight": nest.random.uniform(min=0., max=1.),
                               "delay": 1.})
        nest.Connect(ipop, epop, {"rule": "fixed_indegree", "indegree": inh_connections},
                     syn_spec={"weight": nest.random.uniform(min=-1., max=0.),
                               "delay": 1.})
    else:
        exc_node_info = nest.GetStatus(epop)
        exc_local_nodes = [(ni["global_id"], ni["vp"]) for ni in exc_node_info if ni["local"]]
        inh_node_info = nest.GetStatus(ipop)
        inh_local_nodes = [(ni["global_id"], ni["vp"]) for ni in inh_node_info if ni["local"]]

    nest.Connect(epop, exc_spike_recorder)
    nest.Connect(ipop, inh_spike_recorder)


def nest_experiment():
    count = 0
    start = perf_counter()
    # Iterate over sizes
    for exc_connections in range(1, POPULATION_SIZE + 1):
        for inh_connections in range(1, POPULATION_SIZE + 1):
            sim_name = "balancedIE_" + str(exc_connections) + "_" + \
                       str(inh_connections)
            create_and_reset_sim_dir(sim_name)
            chdir(sim_name)
            for i in range(1, NUMBER_OF_REPEATS+1):
                count += 1
                kernel_settings()
                balanced_ie_network(POPULATION_SIZE, exc_connections, inh_connections, i)
                nest.Simulate(NEST_SIMULATION_TIME)
                nest.ResetKernel()
            chdir("..")

    for connections in range(1, POPULATION_SIZE + 1):
        sim_name = "selfconnected_" + str(connections)
        create_and_reset_sim_dir(sim_name)
        chdir(sim_name)
        for i in range(0, NUMBER_OF_REPEATS):
            count += 1
            kernel_settings()
            self_connected_network(POPULATION_SIZE, connections, i)
            nest.Simulate(NEST_SIMULATION_TIME)
            nest.ResetKernel()
        chdir("..")

    total_time = round(perf_counter() - start, 2)
    print(str(count) + " experiments performed in " + str(total_time) + " seconds.")


def main():
    if isdir("nest_results"):
        rmtree("nest_results")
    mkdir("nest_results")
    chdir("nest_results")
    print("---NEST EXPERIMENT START---")
    nest_experiment()
    compile_data()
    print("---NEST EXPERIMENT END---")


def run_nest_experiment():
    main()


if __name__ == "__main__":
    main()
