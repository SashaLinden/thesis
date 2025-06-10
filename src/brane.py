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


def parse_results(results: list) -> dict:
    container_creation = []
    container_launching = []
    container_runtime = []
    total_runtime = []

    previous_line = ""

    for line in results:
        if CONTAINER_CREATION in line:
            container_creation.append(line.replace(CONTAINER_CREATION, ""))
        elif CONTAINER_LAUNCHING in line:
            container_launching.append(line.replace(CONTAINER_LAUNCHING, ""))
        elif CONTAINER_RUNTIME in line:
            container_runtime.append(line.replace(CONTAINER_RUNTIME, ""))
        elif (
            TOTAL_CONTAINER_TIME_PREV in previous_line and TOTAL_CONTAINER_TIME in line
        ):
            total_runtime.append(line.replace(TOTAL_CONTAINER_TIME, ""))
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

    container_creation = [convert_to_microseconds(x) for x in container_creation]
    container_launching = [convert_to_microseconds(x) for x in container_launching]
    container_runtime = [convert_to_microseconds(x) for x in container_runtime]
    total_runtime = [convert_to_microseconds(x) for x in total_runtime]

    return {
        "container_creation": container_creation,
        "container_launching": container_launching,
        "container_runtime": container_runtime,
        "total_runtime": total_runtime,
    }


def plot_runtime(results: dict, file: str):
    plt.figure(figsize=(12, 7))
    x = np.arange(len(results["total_runtime"]))
    width = 0.2

    plt.bar(
        x - 1.5 * width,
        results["total_runtime"],
        width,
        label="Total Runtime",
        color="blue",
    )
    plt.bar(
        x - 0.5 * width,
        results["container_creation"],
        width,
        label="Container Creation",
        color="orange",
    )
    plt.bar(
        x + 0.5 * width,
        results["container_launching"],
        width,
        label="Container Launching",
        color="green",
    )
    plt.bar(
        x + 1.5 * width,
        results["container_runtime"],
        width,
        label="Container Runtime",
        color="red",
    )

    plt.title(f"Runtime Analysis for {file}")
    plt.xlabel("Run Number")
    plt.ylabel("Time (microseconds)")
    plt.xticks(x, np.arange(1, len(results["total_runtime"]) + 1))
    plt.legend()
    plt.grid(axis="y")
    plt.tight_layout()


def main():
    files = ["hello_world", "hello_world10"]

    results = {}
    # Initialize results dictionary
    for i in files:
        results[i] = {}

    # Run benchmarks for each file 50 times
    # for _ in trange(50, desc="Benchmark rounds"):
    #     for file in files:
    #         result = run_benchmark(file)
    #         parsed_results = parse_results(result)
    #         for key in parsed_results:
    #             if key not in results[file]:
    #                 results[file][key] = [parsed_results[key]]
    #             else:
    #                 results[file][key].append(parsed_results[key])
    # with open("results.pkl", "wb") as f:
    #     pickle.dump(results, f)

    with open("results.pkl", "rb") as f:
        results = pickle.load(f)
    # pprint.pp(results)
    # Calculate average results
    average_results = {}
    for file in files:
        average_results[file] = {
            "container_creation": [],
            "container_launching": [],
            "container_runtime": [],
            "total_runtime": [],
        }
    for file in files:
        average_results[file]["container_creation"] = np.mean(
            results[file]["container_creation"], axis=0
        )
        average_results[file]["container_launching"] = np.mean(
            results[file]["container_launching"], axis=0
        )
        average_results[file]["container_runtime"] = np.mean(
            results[file]["container_runtime"], axis=0
        )
        average_results[file]["total_runtime"] = np.mean(
            results[file]["total_runtime"], axis=0
        )
    # Round all values to 2 decimals
    for file in average_results:
        for key in average_results[file]:
            average_results[file][key] = np.round(average_results[file][key], 2)
    pprint.pp(average_results)

    for file in files:
        plot_runtime(average_results[file], file)

    plt.show()


if __name__ == "__main__":
    main()
