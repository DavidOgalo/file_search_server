import matplotlib.pyplot as plt

def parse_benchmark_results(file_path):
    with open(file_path, 'r') as f:
        lines = f.readlines()

    # Skip the header lines
    lines = lines[2:]

    # Prepare data structure
    results = {}

    for line in lines:
        parts = line.strip().split()
        if len(parts) == 3:
            algorithm = parts[0]
            size = int(parts[1])
            time = float(parts[2])

            if algorithm not in results:
                results[algorithm] = []
            results[algorithm].append((size, time))

    return results

def plot_results(results):
    plt.figure(figsize=(10, 6))

    for algorithm, data in results.items():
        data = sorted(data)  # Ensure data is sorted by file size
        sizes, times = zip(*data)
        plt.plot(sizes, times, marker='o', label=algorithm)

    plt.xlabel('File Size')
    plt.ylabel('Execution Time (s)')
    plt.title('Execution Time vs. File Size for Different Algorithms')
    plt.legend()
    plt.grid(True)
    plt.savefig('benchmark_chart.png')
    plt.show()

# Parse the benchmark results
benchmark_results = parse_benchmark_results('benchmark_results.txt')

# Plot the results
plot_results(benchmark_results)
