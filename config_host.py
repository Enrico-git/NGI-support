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
        if self.gender.lower() != 'test' and self.gender.lower() != 'train':
            print('insert test or train only!')
            exit(-2)
        self.num_iperf=int(sys.argv[2])
        self.hostname=sys.argv[3]
        self.list_ip=sys.argv[4].split(',')
        self.svr_num = int(len(self.list_ip)/3) #svs = last 'svr_num' from the list
        if self.svr_num == 0:
            self.svr_num = 1
        self.cl_num = int(len(self.list_ip) - self.svr_num)
        
        # NOTE: last addresses in the list are used as iperf3 -s
        self.ip_svrs = self.list_ip[-self.svr_num:]
        self.num_port_each_svr = int(self.cl_num/self.svr_num)

        #Grab IP host
        proc = subprocess.run(['hostname', '-I'], stdout=subprocess.PIPE, universal_newlines=True)
        list_addresses = proc.stdout.split(' ')
        self.my_addr = list(filter(lambda el: el.startswith('192.168'), list_addresses))[0]

        self.num_load = 10 # from 10 Mbps to 100 Mbps
        self.first_port=6969
        random.seed(19951018+int(self.hostname[1:]))
        
    def run_server(self, port):
        #run one thread for each port
        server = iperf3.Server()
        server.bind_address=self.my_addr
        server.port=port
        with open('file', 'a') as sys.stdout:
            print(f'iperf3 -s from {self.my_addr}, port {port}')
        while True:
            test = server.run()
            with open('file', 'a') as sys.stdout:
                print(test)

    def generate_traffic(self):        
        if self.my_addr in self.ip_svrs: #one of the server
            index = self.ip_svrs.index(self.my_addr)
            processes = []
            if self.my_addr != self.ip_svrs[-1]:
                #run num port needed for each server
                for i in range(self.num_port_each_svr): #One thread for each port!
                    proc_port = self.first_port + (index * self.num_port_each_svr) + i
                    proc = Process(target=self.run_server, args=(proc_port, ) )
                    processes.append(proc)
                    proc.start()
                for i in range(self.num_port_each_svr):
                    processes[i].join()
            else:
                #run num_port_each_svr + what it rests
                remaining_port = (self.cl_num - (index * self.num_port_each_svr))
                for i in range(remaining_port): #One thread for each port!
                    proc_port = self.first_port + (index * self.num_port_each_svr)  + i
                    proc = Process(target=self.run_server, args=(proc_port, ) )
                    processes.append(proc)
                    proc.start()
                for i in range(remaining_port):
                    processes[i].join()
        else:
            for j in range(self.num_load): # 20 test at [10, 20, 30, ..., 100] Mbps
                for i in range(self.num_iperf):
                    print(f'iteration {i}/{self.num_iperf}, {(j+1)*10}Mbps')
                    # generate a random iperf3 request: f(t, bw, svr)
                    client = iperf3.Client()
                    client.port=self.first_port + int(self.hostname[1:])
                    client.bandwidth = 10 * (j + 1) * 1024 * 1024 #Mbps
                    
                    #find which server open the selected port
                    for k in range(self.svr_num):
                        start_range_port_svr = self.first_port + (k * self.num_port_each_svr)
                        end_range_port_svr = start_range_port_svr + self.num_port_each_svr
                        if k == (self.svr_num -1):
                            remaining_port = (self.cl_num - (k * self.num_port_each_svr))
                            end_range_port_svr = start_range_port_svr + remaining_port + 1 
                        if client.port >= start_range_port_svr and client.port < end_range_port_svr:
                            client.server_hostname = self.ip_svrs[k]
                            break
                    if self.hostname != 'h0':
                        client.duration = random.randint(10, 20)
                    else:
                        client.duration = 15

                    while True:
                        print(f'iperf to {client.server_hostname}, bw: {client.bandwidth}bps, time: {client.duration}s')
                        test = client.run()
                        if test.error == None:
                            json_test = test.json
                            Mbps = test.sent_Mbps
                            mean_rtt=json_test['end']['streams'][0]['sender']['mean_rtt']
                            print(f'Mbps: {Mbps}, mean_rtt: {mean_rtt}')
                            if self.gender.lower() == 'test' and self.hostname == 'h0':
                                #save measurement on file.
                                Mbps = int((client.bandwidth/1024)/1024)
                                filename = 'iperf3_Mb'+str(Mbps)+'_it'+str(i)+'.json'
                                with open(filename, "w") as file1:
                                    # Writing data to a file
                                    file1.write(json.dumps(json_test))
                            break
                        else:
                            print(test.error)
                            time.sleep(10)
                            continue
                    del client
                    time.sleep(random.randint(1, 5))
                    

if __name__ == '__main__':
    if len(sys.argv) < 5:
        print('usage: python3 config_host.py <train/test> <num_iperf> <hostnameID> <ip1>,<ipN>')
        exit(-1)
    tf = TrafficGenerator()
    tf.generate_traffic()
    

#python3 NGI-support-main/config_host.py train 10 h0 192.168.0.4,192.168.0.6,192.168.0.10,192.168.0.12,192.168.0.16,192.168.0.18
#python3 NGI-support-main/config_host.py test 15 h0 192.168.0.4,192.168.0.6,192.168.0.10,192.168.0.12,192.168.0.16,192.168.0.18
