import time
import requests
import threading


def get_request(url, n, thread_name):
    start = time.perf_counter()
    for i in range(n):
        status = requests.get(url)
        print(status)
    end = time.perf_counter()
    print(f'{thread_name}: deltatime - {end-start}')


if __name__ == "__main__":
    start_time = time.perf_counter()
    print(f'Start executing: {start_time}')
    n = 5   # Number of requests
    threads = 5   # Number of threads to create
    url = 'https://app-perf.example.com/api/v1/meta/version'
    jobs = []
    for i in range(0, threads):
        thread_name = f'thread {i}'
        thread = threading.Thread(target=get_request(url, n, thread_name))
        jobs.append(thread)

    # Start the threads (i.e. calculate the random number lists)

    for j in jobs:
        j.start()
    # Ensure all of the threads have finished
    for j in jobs:
        j.join()

    end_time = time.perf_counter()
    print(f'End executing: {end_time}')
    print(f'Total spent time: {end_time - start_time}')