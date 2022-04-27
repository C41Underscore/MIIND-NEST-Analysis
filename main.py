from nest_experiment import run_nest_experiment
from miind_experiment import run_miind_experiment
from time import perf_counter


def main():
    start = perf_counter()
    run_nest_experiment()
    run_miind_experiment()
    end = perf_counter() - start
    print("---\nProgram executed in " + str(end) + " seconds.\n---")


if __name__ == "__main__":
    main()
