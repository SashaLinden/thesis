import subprocess

CONTAINER_CREATION = "Container creation timing results: "
CONTAINER_LAUNCHING = "Container launching timing results: "
CONTAINER_RUNTIME = "Container runtime timing results: "


def run_benchmark(file):
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


def parse_results(results):
    container_creation = []
    container_launching = []
    container_runtime = []

    for line in results:
        if CONTAINER_CREATION in line:
            container_creation.append(line.replace(CONTAINER_CREATION, ""))
        elif CONTAINER_LAUNCHING in line:
            container_launching.append(line.replace(CONTAINER_LAUNCHING, ""))
        elif CONTAINER_RUNTIME in line:
            container_runtime.append(line.replace(CONTAINER_RUNTIME, ""))

    def convert_to_microseconds(value):
        if value.endswith("us"):
            return int(value[:-2])
        elif value.endswith("ms"):
            return int(value[:-2]) * 1000
        else:
            raise ValueError(f"Unexpected time format: {value}")

    container_creation = [convert_to_microseconds(x) for x in container_creation]
    container_launching = [convert_to_microseconds(x) for x in container_launching]
    container_runtime = [convert_to_microseconds(x) for x in container_runtime]

    return {
        "container_creation": container_creation,
        "container_launching": container_launching,
        "container_runtime": container_runtime,
    }


def main():
    files = ["hello_world", "hello_world10"]

    results = {}
    for i in files:
        results[i] = []

    for _ in range(50):
        for file in files:
            result = run_benchmark(file)
            parsed_results = parse_results(result)
            results[file].append(parsed_results)


if __name__ == "__main__":
    main()
