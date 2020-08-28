import time
import requests
import argparse
import multiprocessing


def get_request(url, n, proc_name):
    start = time.perf_counter()
    for i in range(n):
        status = requests.get(url)
        print(status)
    end = time.perf_counter()
    print(f'{proc_name}: deltatime - {end-start}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process some integers.')
    start_time = time.perf_counter()
    print(f'Start executing: {start_time}')
    n = 5  # Number of requests
    procs = 5  # Number of threads to create
    url = 'https://app-perf.example.com/api/v1/meta/version'

    # Create a list of jobs and then iterate through
    # the number of processes appending each process to
    # the job list
    jobs = []
    for i in range(0, procs):
        proc_name = f'proc {i}'
        process = multiprocessing.Process(target=get_request,
                                          args=(url, i, proc_name))
        jobs.append(process)

    # Start the processes (i.e. calculate the random number lists)
    for j in jobs:
        j.start()

    # Ensure all of the processes have finished
    for j in jobs:
        j.join()

    end_time = time.perf_counter()
    print(f'End executing: {end_time}')
    print(f'Total spent time: {end_time - start_time}')