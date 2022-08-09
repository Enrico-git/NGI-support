import sys
import random
import subprocess
import time
import iperf3
from multiprocessing import Process
import json

class TrafficGenerator:

    def __init__(self):
        self.hostname=sys.argv[1]
        self.list_ip=sys.argv[2].split(',')
        self.svr_num = int(len(self.list_ip)/3) #svs = last 'svr_num' from the list
        self.cl_num = int(len(self.list_ip) - self.svr_num)

        #Grab IP host
        proc = subprocess.run(['hostname', '-I'], stdout=subprocess.PIPE, universal_newlines=True)
        list_addresses = proc.stdout.split(' ')
        self.my_addr = list(filter(lambda el: el.startswith('192.168'), list_addresses))[0]

        self.iperf_time = 60    # seconds
        self.num_iperf = 60*10  # 1 min * 10 = 10 min * 6 = 1 h * 6 = 6h
        self.first_port=6969
        random.seed(19951018+int(self.hostname[1:]))
        
    def run_server(self, port):
        #run one thread for each port
        server = iperf3.Server()
        server.bind_address=self.my_addr
        server.port=port
        print(f'iperf3 -s from {self.my_addr}, port {port}')
        while True:
            test = server.run()
            print(test)

    def generate_traffic(self):
        # NOTE: last addresses in the list are used as iperf3 -s
        if self.my_addr in self.list_ip[-self.svr_num:]: #one of the server
            processes = []
            for i in range(self.cl_num): #One thread for each port!
                proc_port = self.first_port + i
                proc = Process(target=self.run_server, args=(proc_port, ) )
                processes.append(proc)
                proc.start()
            for i in range(self.cl_num):
                processes[i].join()
        else:
            for i in range(self.num_iperf):
                print(f'iteration {i}/{self.num_iperf}')
                # generate a random iperf3 request: f(t, bw, svr)
                client = iperf3.Client()
                client.port=self.first_port + int(self.hostname[1:])
                client.bandwidth = 10 * 1024 * 1024 #bps
                if self.hostname != 'h0':
                    r_index = -random.randint(1, self.svr_num)   #-1, -2, -N
                    client.server_hostname = self.list_ip[r_index]  
                    #client.bandwidth = random.randint(1, 10)
                    client.duration = random.randint(30, 90)
                else: # h0 does static request to the last server only
                    client.server_hostname = self.list_ip[-1]
                    client.duration = 120
                
                while True:
                    print(f'iperf to {client.server_hostname}, bw: {client.bandwidth}, time: {client.duration}')
                    test = client.run()
                    if test.error == None:
                        json_test = test.json
                        bps = json_test['end']['streams'][0]['sender']['bits_per_second']
                        max_rtt=json_test['end']['streams'][0]['sender']['max_rtt']
                        min_rtt=json_test['end']['streams'][0]['sender']['min_rtt']
                        mean_rtt=json_test['end']['streams'][0]['sender']['mean_rtt']
                        print(f'bps: {bps}, mean_rtt: {mean_rtt}')
                        if self.hostname == 'h0':
                            #save measurement on file.
                            Mbps = int((client.bandwidth/1024)/1024)
                            filename = 'iperf3_b'+str(Mbps)+'_it'+str(i)+'.json'
                            with open(filename, "w") as file1:
                                # Writing data to a file
                                file1.write(json.dumps(json_test))
                        break
                    else:
                        time.sleep(15)
                        continue
                del client
                time.sleep(random.randint(1, 10))

if __name__ == '__main__':
    tf = TrafficGenerator()
    tf.generate_traffic()
    

#python3 config_host.py h0 192.168.0.4,192.168.0.6,192.168.0.10,192.168.0.12,192.168.0.16,192.168.0.18
