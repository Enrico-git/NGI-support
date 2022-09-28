#This is for 4SW topology. 
# h0-h4
# h1-h5
# h2-h5
# h3-h5

import sys
import random
import subprocess
import time
import iperf3
from multiprocessing import Process
import json

class TrafficGenerator:

    def __init__(self):
        self.gender=sys.argv[1]
        if self.gender.lower() != 'tput' and self.gender.lower() != 'rtt':
            print('insert tput or rtt only!')
            exit(-2)
        self.num_iperf=int(sys.argv[2])
        
        self.list_ip=sys.argv[3].split(',')
        self.svr_num = 2
        self.cl_num = 4
        
        # NOTE: last addresses in the list are used as iperf3 -s
        self.ip_svrs = self.list_ip[-self.svr_num:]
        self.num_port_each_svr = int(self.cl_num/self.svr_num)

        #Grab IP host
        proc = subprocess.run(['hostname', '-I'], stdout=subprocess.PIPE, universal_newlines=True)
        list_addresses = proc.stdout.split(' ')
        self.my_addr = list(filter(lambda el: el.startswith('192.168'), list_addresses))[0]

        self.hostname='h'+str(self.list_ip.index(self.my_addr))

        self.num_load = 10 # from 10 Mbps to 100 Mbps
        self.first_port=6969
        random.seed(19951018+int(self.hostname[1:]))
        
    def run_server(self, port):
        #only h4 can run netserver for latency. the other must generate traffic
        if self.hostname == 'h4' and self.gender == 'rtt':
            #kill previous
            subprocess.run(['sudo', 'pkill', 'netserver'],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            #start process in background
            print(f'netserver -4 in {self.my_addr}, port {port}')
            subprocess.run(['sudo', 'netserver', '-4', '-p', f'{port}'],
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            #run one thread for each port
            server = iperf3.Server()
            server.bind_address=self.my_addr
            server.port=port
            print(f'iperf3 -s from {self.my_addr}, port {port}')
            while True:
                test = server.run()
                print(test)
        

    def generate_traffic(self):        
        if self.my_addr in self.ip_svrs: #one of the server
            processes = []
            if self.hostname == 'h4':
                for i in range(1):
                    proc_port = self.first_port # 6969=h0
                    proc = Process(target=self.run_server, args=(proc_port, ) )
                    processes.append(proc)
                    proc.start()
                for i in range(1):
                    processes[i].join()
            elif self.hostname == 'h5':
                for i in range(3):
                    proc_port = self.first_port + 1 + i # 6970=h1, 6971=h2, 6972=h3
                    proc = Process(target=self.run_server, args=(proc_port, ) )
                    processes.append(proc)
                    proc.start()
                for i in range(3):
                    processes[i].join()
        else: #client
            for j in range(self.num_load): # 20 test at [10, 20, 30, ..., 100] Mbps
                for i in range(self.num_iperf):
                    print(f'iteration {i}/{self.num_iperf}, {(j+1)*10}Mbps')
                    if self.hostname == 'h0' and self.gender == 'rtt':
                        server_hostname = self.ip_svrs[0]    #h6
                        port=self.first_port + int(self.hostname[1:])
                        duration=20

                        print(f'netperf -H {server_hostname} -p {port} -l {duration} -t TCP_RR -- -o mean_latency')
                        proc = subprocess.run(['netperf', '-H', f'{server_hostname}', '-p', f'{port}',
                                        '-l', f'{duration}', '-t', 'TCP_RR', '--', '-o', 'mean_latency'],
                            stdout=subprocess.PIPE, universal_newlines=True)
                        mean_rtt = proc.stdout.split('\n')[-2]
                        print(f'mean_rtt: {mean_rtt}')
                        #save measurement on file.
                        filename = 'netperf_latency.txt'
                        with open(filename, "a") as file1:
                            file1.write(json.dumps(mean_rtt)+'\n')
                    else:
                        client = iperf3.Client()
                        client.port=self.first_port + int(self.hostname[1:])
                        client.bandwidth = 10 * (j + 1) * 1024 * 1024 #Mbps
                        client.duration = 20 # seconds
                        if self.hostname == 'h0':
                            client.server_hostname = self.ip_svrs[0]    #h4
                        else:
                            client.server_hostname = self.ip_svrs[1]    #h5
                        
                        while True:
                            print(f'iperf to {client.server_hostname}, bw: {client.bandwidth}bps, time: {client.duration}s')
                            test = client.run()
                            if test.error == None:
                                json_test = test.json
                                filename = self.hostname+'_iperf3_total.txt'
                                with open(filename, "a") as file1:
                                    file1.write(json.dumps(json_test)+'\n')
                                break
                            else:
                                print(test.error)
                                time.sleep(10)
                                continue
                        del client
                        time.sleep(random.randint(1, 5))
                    

if __name__ == '__main__':
    if len(sys.argv) < 4:
        print('usage: python3 config_host.py <tput/rtt> <num_iperf> <ip1>,<ipN>')
        exit(-1)
    tf = TrafficGenerator()
    tf.generate_traffic()
    

#python3 NGI-support-main/config_host.py train 10 h0 192.168.0.4,192.168.0.6,192.168.0.10,192.168.0.12,192.168.0.16,192.168.0.18
#python3 NGI-support-main/config_host.py test 15 h0 192.168.0.4,192.168.0.6,192.168.0.10,192.168.0.12,192.168.0.16,192.168.0.18
