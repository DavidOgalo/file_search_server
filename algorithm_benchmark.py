import time
import random
import string
import os

# Define the search algorithms
def naive_search(data, query):
    return [line.strip() for line in data if line.strip() == query]

def binary_search(data, query):
    sorted_data = sorted(line.strip() for line in data)
    low, high = 0, len(sorted_data) - 1
    while low <= high:
        mid = (low + high) // 2
        if sorted_data[mid] == query:
            return [sorted_data[mid]]
        elif sorted_data[mid] < query:
            low = mid + 1
        else:
            high = mid - 1
    return []

def kmp_search(data, query):
    def compute_lps(pattern):
        lps = [0] * len(pattern)
        length = 0
        i = 1
        while i < len(pattern):
            if pattern[i] == pattern[length]:
                length += 1
                lps[i] = length
                i += 1
            else:
                if length != 0:
                    length = lps[length - 1]
                else:
                    lps[i] = 0
                    i += 1
        return lps

    results = []
    lps = compute_lps(query)
    for line in data:
        line = line.strip()
        i = j = 0
        while i < len(line):
            if query[j] == line[i]:
                i += 1
                j += 1
            if j == len(query):
                results.append(line)
                j = lps[j - 1]
            elif i < len(line) and query[j] != line[i]:
                if j != 0:
                    j = lps[j - 1]
                else:
                    i += 1
    return results

def boyer_moore_search(data, query):
    def bad_char_table(pattern):
        table = {}
        for i in range(len(pattern) - 1):
            table[pattern[i]] = len(pattern) - 1 - i
        return table

    def good_suffix_table(pattern):
        table = [0] * len(pattern)
        last_prefix = len(pattern)
        for i in range(len(pattern) - 1, -1, -1):
            if is_prefix(pattern, i + 1):
                last_prefix = i + 1
            table[len(pattern) - 1 - i] = last_prefix - i + len(pattern) - 1
        for i in range(len(pattern) - 1):
            slen = suffix_length(pattern, i)
            table[slen] = len(pattern) - 1 - i + slen
        return table

    def is_prefix(pattern, p):
        j = 0
        for i in range(p, len(pattern)):
            if pattern[i] != pattern[j]:
                return False
            j += 1
        return True

    def suffix_length(pattern, p):
        length = 0
        j = len(pattern) - 1
        for i in range(p, -1, -1):
            if pattern[i] == pattern[j]:
                length += 1
                j -= 1
            else:
                break
        return length

    bad_char = bad_char_table(query)
    good_suffix = good_suffix_table(query)

    results = []
    for line in data:
        line = line.strip()
        i = len(query) - 1
        while i < len(line):
            j = len(query) - 1
            while j >= 0 and line[i] == query[j]:
                i -= 1
                j -= 1
            if j < 0:
                results.append(line)
                i += len(query) + 1
            else:
                i += max(good_suffix[len(query) - 1 - j], bad_char.get(line[i], len(query)))
    return results

def rabin_karp_search(data, query):
    q = 101  # A prime number
    d = 256  # Number of characters in the input alphabet
    m = len(query)
    h = pow(d, m-1) % q
    p = 0
    results = []

    for line in data:
        n = len(line)
        t = 0
        for i in range(m):
            p = (d * p + ord(query[i])) % q
            t = (d * t + ord(line[i])) % q

        for i in range(n - m + 1):
            if p == t:
                if line[i:i+m] == query:
                    results.append(line)
            if i < n - m:
                t = (d * (t - ord(line[i]) * h) + ord(line[i + m])) % q
                if t < 0:
                    t += q

    return results

# Generate a large test file
def generate_test_file(file_path, num_lines):
    with open(file_path, 'w') as f:
        for _ in range(num_lines):
            line = ''.join(random.choices(string.ascii_letters + string.digits, k=20))
            f.write(line + '\n')

# Benchmark different search algorithms
def benchmark_search_algorithms():
    results = []
    algorithms = {
        'naive': naive_search,
        'binary': binary_search,
        'kmp': kmp_search,
        'boyer_moore': boyer_moore_search,
        'rabin_karp': rabin_karp_search,
    }

    # File sizes for benchmarking
    file_sizes = [10000, 50000, 100000, 200000, 500000, 1000000]

    for file_size in file_sizes:
        file_path = f'./test_file_{file_size}.txt'
        generate_test_file(file_path, file_size)

        with open(file_path, 'r') as file:
            data = file.readlines()

        for algorithm_name, algorithm_func in algorithms.items():
            start_time = time.time()
            query = ''.join(random.choices(string.ascii_letters + string.digits, k=20))
            algorithm_func(data, query)
            end_time = time.time()
            execution_time = end_time - start_time
            results.append((file_size, algorithm_name, execution_time))
            print(f'Algorithm: {algorithm_name}, File Size: {file_size}, Execution Time: {execution_time:.4f}s')

        os.remove(file_path)

    return results

# Run the benchmark and save the results
benchmark_results = benchmark_search_algorithms()

# Save results to a file for the speed report
with open('benchmark_results.txt', 'w') as f:
    for result in benchmark_results:
        f.write(f'File Size: {result[0]}, Algorithm: {result[1]}, Execution Time: {result[2]:.4f}s\n')
