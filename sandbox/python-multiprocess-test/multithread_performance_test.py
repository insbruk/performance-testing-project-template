import time
import requests
import threading
import uuid


def get_request(start, end):
    session = requests.session()
    for i in range(start, end):
        url = f'http://apiq.example.com:8094/checkUserLogin?username=perftest@example.com'
        r = session.get(url)
        print(url, r.status_code, r.elapsed.total_seconds())


if __name__ == "__main__":
    start = 100000
    end = 1000000
    threads = 500   # Number of threads to create

    jobs = []
    for i in range(0, threads):
        # thread_name = f'thread {i}'
        thread = threading.Thread(target=get_request(start=start, end=end))
        jobs.append(thread)

    # Start the threads (i.e. calculate the random number lists)

    for j in jobs:
        j.start()
    # Ensure all of the threads have finished
    for j in jobs:
        j.join()

    # end_time = time.perf_counter()
    # print(f'End executing: {end_time}')
    # print(f'Total spent time: {end_time - start_time}')