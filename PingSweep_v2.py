#!/usr/bin/env/python3
# -*- coding: UTF-8 -*-
# Original author: MWS
# Creation date: 2021-04-08
# Purpose: Ping Sweep - send 256 pings (from 169.254.187.0 .. 169.254.187.255) and report if it's a live ip address.
#          Runs on Raspberry Pi, starts 59 or 60 threads and takes only 25s to complete.
import os, threading
from queue import Queue
from datetime import datetime

print_lock = threading.Lock() # used to make sure 2 threads can't simultaneously print out
net = '169.254.242.' # base ip address
q = Queue() # queue of jobs to be handled by threads

start_time = datetime.now()

def pinger(ip):
    # step 1: ping the ip address (times out after 1s)
    addr = net + ip
    cmd = 'ping -c 1 ' + addr
    #print(f'{cmd=}')
    out = os.popen(cmd)

    # step 2: if the ping got a response it will contain 'ttl'
    for line in out.readlines():
        # print(f'     {line=}')
        if (line.count('ttl')):
            with print_lock:
                print('********** '+addr+' is live!')

def threader():
    while True:
        # the daemon will continuously get an item off the queue, process it, and mark it as done.
        item = q.get()
        pinger(item)
        q.task_done()

# send some tasks to the threader
for ip in range(0,255):
    q.put(str(ip))
print('Scanning...')

# keep starting more worker threads until there are enough to handle the queue
thread_count = 0
while thread_count < q.qsize():
    threading.Thread(target = threader, daemon=True).start()
    thread_count += 1
    
print(f'started {thread_count} threads.')

# block until all tasks are done
q.join()

end_time = datetime.now()
print(f"All tasks completed. Time taken: {str(end_time-start_time).split('.', 2)[0]}.")
