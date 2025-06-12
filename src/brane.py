import subprocess
import numpy as np
import matplotlib.pyplot as plt
import pprint
from tqdm import trange
import pickle


CONTAINER_CREATION = "Container creation timing results: "
CONTAINER_LAUNCHING = "Container launching timing results: "
CONTAINER_RUNTIME = "Container runtime timing results: "
TOTAL_CONTAINER_TIME_PREV = "brane_cli::vm::OfflinePlugin::execute() timing results:"
TOTAL_CONTAINER_TIME = "Total timing results: "

CREATION = "container_creation"
LAUNCHING = "container_launching"
RUNTIME = "container_runtime"
TOTAL_RUNTIME = "total_runtime"

TIMING_RESULTS = [TOTAL_RUNTIME, LAUNCHING, RUNTIME, CREATION]


def run_benchmark(file: str) -> list:
    command = f"bin/brane workflow run test src/{file}.bs --profile"
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    result_stdout = result.stdout.split("\n")
    result_stdout = [
        line.strip() for line in result_stdout if line.strip()
    ]  # Remove empty lines
    # remove ' - ' from the beginning of each line
    result_stdout = [
        line[2:] if line.startswith("- ") else line for line in result_stdout
    ]

    return result_stdout


def parse_results(lines: list) -> dict:
    results = {}

    for i in TIMING_RESULTS:
        results[i] = []

    previous_line = ""

    for line in lines:
        if CONTAINER_CREATION in line:
            results[CREATION].append(line.replace(CONTAINER_CREATION, ""))
        elif CONTAINER_LAUNCHING in line:
            results[LAUNCHING].append(line.replace(CONTAINER_LAUNCHING, ""))
        elif CONTAINER_RUNTIME in line:
            results[RUNTIME].append(line.replace(CONTAINER_RUNTIME, ""))
        elif (
            TOTAL_CONTAINER_TIME_PREV in previous_line and TOTAL_CONTAINER_TIME in line
        ):
            results[TOTAL_RUNTIME].append(line.replace(TOTAL_CONTAINER_TIME, ""))
        previous_line = line

    def convert_to_microseconds(value):
        if value.endswith("us"):
            return int(value[:-2])
        elif value.endswith("ms"):
            return int(value[:-2]) * 1000
        elif value.endswith("s"):
            return int(value[:-1]) * 1000000
        else:
            raise ValueError(f"Unexpected time format: {value}")

    for i in TIMING_RESULTS:
        if not results[i]:
            raise ValueError(f"No results found for {i}")
        results[i] = [convert_to_microseconds(x) for x in results[i]]

    return results


def plot_runtime(results: dict, file: str):
    plt.figure(figsize=(12, 7))
    x = np.arange(len(results["total_runtime"]))
    width = 0.2

    for i, j in enumerate(TIMING_RESULTS):
        plt.errorbar(
            x + i * width - width,
            np.mean(results[j], axis=1),
            yerr=np.std(results[j], axis=1),
            fmt="o",
        )
        plt.bar(
            x + i * width - width,
            np.mean(results[j], axis=1),
            width=width,
            yerr=np.std(results[j], axis=1),
            alpha=0.5,
            label=j.replace("_", " ").title(),
        )

    plt.title(f"Runtime Analysis for {file}")
    plt.xlabel("Run Number")
    plt.ylabel("Time (microseconds)")
    plt.xticks(x, np.arange(1, len(results["total_runtime"]) + 1))
    plt.legend()
    plt.grid(axis="y")
    plt.tight_layout()


def main():
    files = ["prime"]

    results = {}
    # Initialize results dictionary
    for i in files:
        results[i] = {}

    # Run benchmarks for each file 50 times
    for _ in trange(50, desc="Benchmark rounds"):
        for file in files:
            result = run_benchmark(file)
            parsed_results = parse_results(result)
            for key in parsed_results:
                if key not in results[file]:
                    results[file][key] = [parsed_results[key]]
                else:
                    results[file][key].append(parsed_results[key])
    with open("results50prime.pkl", "wb") as f:
        pickle.dump(results, f)

    # with open("results.pkl", "rb") as f:
    #     results = pickle.load(f)

    # Calculate average results
    total_results = {}
    for file in files:
        total_results[file] = {metric: [] for metric in TIMING_RESULTS}

    for file in files:
        for metric in TIMING_RESULTS:
            # Group values by index for each metric
            total_results[file][metric] = [list(x) for x in zip(*results[file][metric])]

    for file in files:
        plot_runtime(total_results[file], file)

    plt.show()


if __name__ == "__main__":
    main()
