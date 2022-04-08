from nest_experiment import run_nest_experiment
from miind_experiment import run_miind_experiment

# TODO: Run experiments with small samples, examine the data to see if the experiments are producing reasonable results
# TODO: Produce script for analysis
# TODO: Get MIIND running with reduced parameters and new set up
# TODO: Automate removal of redundant data files


def main():
    run_nest_experiment()
    run_miind_experiment()


if __name__ == "__main__":
    main()
