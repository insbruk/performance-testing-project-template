import os
import time
import psutil
import requests
import argparse
import multiprocessing


def get_cpu_utilization():
    return psutil.cpu_percent(interval=1)


def get_mem_utilization():
    return psutil.virtual_memory().percent


def collect_resource_utilization(prefix=''):
    cpu_util_log = f'{prefix}u_cpu_utilization.csv'
    mem_util_log = f'{prefix}u_mem_utilization.csv'
    cpu_util_log_file = open(cpu_util_log, mode='w')
    cpu_util_log_file.write('date,time,cpu_utilization\n')
    cpu_util_log_file.close()
    mem_util_log_file = open(mem_util_log, mode='w')
    mem_util_log_file.write('date,time,mem_utilization\n')
    mem_util_log_file.close()
    while True:
        cpu_util_log_file = open(cpu_util_log, mode='a')
        mem_util_log_file = open(mem_util_log, mode='a')
        dt = time.strftime('%Y-%m-%d')
        tm = time.strftime('%H:%M:%S')
        cpu = f'"{dt}","{tm}",{get_cpu_utilization()}\n'
        mem = f'"{dt}","{tm}",{get_mem_utilization()}\n'
        cpu_util_log_file.write(cpu)
        mem_util_log_file.write(mem)
        cpu_util_log_file.close()
        mem_util_log_file.close()
        time.sleep(1)


def login():
    auth_url = 'https://app-perf.example.com/api/v1/sso/jwt/login'
    json_txt = '{"claimParams":{"name":"Ivanov,Ivan","userrole":"ADMIN"},"clientId":"4fff517b-194b-456c-91e2-6245ca7121ab","clientSecret":"62661fae-6ecb-4f72-a745-49120b360dda","subject":"perftest@example.com"}'
    headers = {
        'Content-type': 'application/json'
    }
    r = requests.post(url=auth_url,
                      data=json_txt,
                      headers=headers)
    return r.json()['token']


def request(url, num_of_requests, think_time):
    auth_cookie = login()
    auth_cookie = {
        'X-NG-ADMIN-JWT-TOKEN': auth_cookie
    }
    session = requests.session()
    headers = {
        'Content-type': 'application/json'
    }
    data = '{"resultLimit":500,"courseType":"example","institution":null,"productId":null,"courseName":"Any","institutionId":null}'

    requests_log = 'requests.csv'
    requests_log_file = open(requests_log, 'w')
    requests_log_file.write('PID,date,time,request,response_status,response_time\n')
    requests_log_file.close()

    for n in range(num_of_requests):
        requests_log_file = open(requests_log, 'a')
        dt = time.strftime('%Y-%m-%d')
        tm = time.strftime('%H:%M:%S')
        response = session.post(url=url,
                                data=data,
                                headers= headers,
                                cookies=auth_cookie)
        rq = f'"PID {os.getpid()}","{dt}","{tm}","POST {url} HTTP/1.1",{response.status_code},{response.elapsed.total_seconds()}\n'
        requests_log_file.write(rq)
        requests_log_file.close()
        print(rq)
        time.sleep(think_time)


if __name__ == '__main__':
    # python --url=http://example.com --processes=10 --requests_per_process=20 --think_time=3
    parser = argparse.ArgumentParser(description='tool for testing multiprocessing with pure python')
    parser.add_argument('--url', type=str, help='target url')
    parser.add_argument('--processes', type=int, help='number of processes')
    parser.add_argument('--requests', type=int, help='number of requests per process')
    parser.add_argument('--think_time', type=int, help='think time between requests')

    args = parser.parse_args()

    url = args.url
    processes = args.processes
    num_of_requests = args.requests
    think_time = args.think_time

    # Create a list of jobs and then iterate through the number of
    # processes appending each process to the job list
    jobs = []

    monitor = multiprocessing.Process(target=collect_resource_utilization,
                                      args=(processes, ))
    jobs.append(monitor)

    for p in range(0, processes):
        process = multiprocessing.Process(target=request,
                                          args=(url, num_of_requests, think_time))
        jobs.append(process)

    # Start the processes (i.e. calculate the random number lists)
    for j in jobs:
        j.start()
        time.sleep(1)
    # Ensure all of the processes have finished
    for j in jobs:
        j.join()

