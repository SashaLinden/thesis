import subprocess

CONTAINER_CREATION = "Container creation timing results: "
CONTAINER_LAUNCHING = "Container launching timing results: "
CONTAINER_RUNTIME = "Container runtime timing results: "


def run_benchmark(file):
    command = f"exec/brane workflow run test src/{file}.bs --profile"
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

    return {
        "container_creation": container_creation,
        "container_launching": container_launching,
        "container_runtime": container_runtime,
    }


def main():
    # run bash command
    files = ["hello_world", "hello_world10"]

    for file in files:
        result = run_benchmark(file)
        parsed_results = parse_results(result)
        print(f"Results for {file}:")
        print("Container Creation:", parsed_results["container_creation"])
        print("Container Launching:", parsed_results["container_launching"])
        print("Container Runtime:", parsed_results["container_runtime"])


if __name__ == "__main__":
    main()
