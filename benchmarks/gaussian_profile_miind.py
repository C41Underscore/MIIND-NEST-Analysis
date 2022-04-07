import matplotlib.pyplot as plt
from os import system, chdir, popen, remove, listdir
from shutil import rmtree
from string import Template
from statistics import mean, median
import miind.miindsim as miind

sigmas = [0.1, 0.3, 0.5, 0.7, 0.9]
mus = [0.1 + i*0.1 for i in range(0, 10)]
TAU = 0.05

GENERATE_FILES = False


def clean_dir():
    chdir("miind_gaussian_files")
    small_sigma = "small_sigma_gaussian_template.xml"
    big_sigma = "big_sigma_gaussian_template.xml"
    files = listdir()
    for file in files:
        if file != small_sigma and file != big_sigma:
            try:
                remove(file)
            except IsADirectoryError:
                rmtree(file)
    chdir("..")


# generate-lif-mesh
# generate-model
# generate-empty-fid
# generate-matrix
def generate_simulation_files(name, efficacy):
    miind_filegen_cmds = ["sim %s.xml" % sim_name,
                          "generate-lif-mesh %s %f 1. 0. -1. 0.001 750" % (name, TAU),
                          "generate-model %s 0. 1." % name,
                          "generate-empty-fid %s" % name,
                          "generate-matrix %s %f 100 0.0 0.0 true" % (name, efficacy)
                          ]
    for cmd in miind_filegen_cmds:
        system("python3 -m miind.miindio " + cmd)


if GENERATE_FILES:
    clean_dir()
    chdir("miind_gaussian_files")
    # create XML file
    count = 0
    for sigma in sigmas:
        for mu in mus:
            sim_name = "gaussian" + str(count)
            if sigma < 0.5:
                h = round((sigma**2)/mu, 3)
                v = (mu**2)/(TAU*sigma**2)
                generate_simulation_files(sim_name, h)
                entire_file = ""
                with open("small_sigma_gaussian_template.xml", "r") as template:
                    for line in template:
                        entire_file += line
                mat_file = popen("ls " + sim_name + "_*.mat").read().rstrip()
                simulation_xml = Template(entire_file)
                simulation_xml = simulation_xml.substitute({
                    "details": str("sigma: " + str(round(sigma, 2)) + " mu: " + str(round(mu, 2))),
                    "sim_name": sim_name,
                    "model_file": sim_name + ".model",
                    "mat_file": mat_file,
                    "exc_rate": str(round(v, 3)),
                    "h": str(round(h, 3)),
                })
                with open(sim_name + ".xml", "w") as sim_file:
                    sim_file.write(simulation_xml)
            else:
                j = 0.1
                v_e = (j*mu + sigma**2)/(2*TAU*j**2)
                v_i = ((j*mu - sigma**2)/(2*TAU*j**2))*-1
                entire_file = ""
                generate_simulation_files(sim_name, j)
                generate_simulation_files(sim_name, -j)
                with open("big_sigma_gaussian_template.xml", "r") as template:
                    for line in template:
                        entire_file += line
                mat_files = popen("ls " + sim_name + "_*.mat").read().rstrip().split("\n")
                matrices = ""
                for file in mat_files:
                    matrices += "<MatrixFile>" + file + "</MatrixFile>\n"
                simulation_xml = Template(entire_file)
                simulation_xml = simulation_xml.substitute({
                    "details": str("sigma: " + str(round(sigma, 2)) + " mu: " + str(round(mu, 2))),
                    "sim_name": sim_name,
                    "model_file": sim_name + ".model",
                    "matrix_files": matrices,
                    "exc_rate": str(round(v_e, 3)),
                    "inh_rate": str(round(v_i, 3)),
                    "j": str(round(j, 3)),
                    "neg_j": str(round(-j, 3))
                })
                with open(sim_name + ".xml", "w") as sim_file:
                    sim_file.write(simulation_xml)
            count += 1
    chdir("..")

chdir("miind_gaussian_files")
count = 0
results = []
for i in sigmas:
    current_results = []
    for j in mus:
        print(count)
        miind.init("gaussian" + str(count) + ".xml", 1)
        timestep = miind.getTimeStep()
        simulation_length = miind.getSimulationLength()
        miind.startSimulation()
        activities = []
        for _ in range(0, int(simulation_length/timestep)):
            activities.append(round(miind.evolveSingleStep([])[0], 3))
        miind.endSimulation()
        current_results.append(mean(activities))
        # try:
        #     with open("gaussian" + str(count) + "_/rate_0", "r") as file:
        #         data = []
        #         for line in file:
        #             data.append(float(line.split("\t")[1]))
        #         current_results.append(mean(data))
        #     count += 1
        # except FileNotFoundError:
        #     with open("rate_0", "r") as file:
        #         data = []
        #         for line in file:
        #             data.append(float(line.split("\t")[1]))
        #         current_results.append(mean(data))
        count += 1
    results.append(current_results)


chdir("..")
with open("gaussians_miind.dat", "w") as file:
    file.write(",".join([str(i) for i in sigmas]) + "\n")
    file.write(",".join([str(round(i, 2)) for i in mus]) + "\n")
    for result in results:
        file.write(",".join([str(round(i, 3)) for i in result]) + "\n")


plt.figure(1)
plt.grid()
for i in range(0, len(sigmas)):
    plt.plot(mus, results[i], label="\u03C3: " + str(sigmas[i]))
plt.legend(loc="upper left")
plt.title("Gaussian Profile (MIIND)")
plt.show()
