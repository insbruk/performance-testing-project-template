import time
import requests
import argparse
import multiprocessing


def get_request(start, end):
    session = requests.session()
    for i in range(start, end):
        url = f'http://apiq.example.com:8094/checkUserLogin?username=perftest@example.com'
        r = session.get(url)
        print(url, r.status_code, r.elapsed.total_seconds())


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process some integers.')
    processes = 150  # Number of threads to create
    jobs = []
    start = 100000
    end = 1000000
    for i in range(0, processes):
        proc_name = f'proc {i}'
        process = multiprocessing.Process(
            target=get_request,
            args=(start, end)
        )
        jobs.append(process)

    # Start the processes (i.e. calculate the random number lists)
    for j in jobs:
        j.start()

    # Ensure all of the processes have finished
    for j in jobs:
        j.join()
