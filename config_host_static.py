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
        self.svr_num = 4 #h6, h7, h8, h9
        self.cl_num = int(len(self.list_ip) - self.svr_num)
        
        # NOTE: last addresses in the list are used as iperf3 -s
        self.ip_svrs = self.list_ip[-self.svr_num:]

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
            processes = []
            if self.hostname == 'h6':
                #run num port needed for each server
                for i in range(2): #One thread for each port!
                    proc_port = self.first_port + i # 6969= h0, 6970=h1
                    proc = Process(target=self.run_server, args=(proc_port, ) )
                    processes.append(proc)
                    proc.start()
                for i in range(2):
                    processes[i].join()
            elif self.hostname == 'h7':
                for i in range(2): #One thread for each port!
                    proc_port = 6973 + i # 6973= h4, 6974=h5
                    proc = Process(target=self.run_server, args=(proc_port, ) )
                    processes.append(proc)
                    proc.start()
                for i in range(2):
                    processes[i].join()
            elif self.hostname == 'h8':
                    proc_port = 6971 # 6971= h2
                    proc = Process(target=self.run_server, args=(proc_port, ) )
                    processes.append(proc)
                    proc.start()
                    processes[0].join()
            elif self.hostname == 'h9':
                    proc_port = 6972 # 6972= h3
                    proc = Process(target=self.run_server, args=(proc_port, ) )
                    processes.append(proc)
                    proc.start()
                    processes[0].join()
        else:
            for j in range(self.num_load): # 20 test at [10, 20, 30, ..., 100] Mbps
                for i in range(self.num_iperf):
                    print(f'iteration {i}/{self.num_iperf}, {(j+1)*10}Mbps')
                    # generate a random iperf3 request: f(t, bw, svr)
                    client = iperf3.Client()
                    client.port=self.first_port + int(self.hostname[1:])
                    client.bandwidth = 10 * (j + 1) * 1024 * 1024 #Mbps
                    
                    #find which server open the selected port
                    if self.hostname == 'h0' or self.hostname == 'h1':
                        client.server_hostname = self.ip_svrs[0]    #h6
                    elif self.hostname == 'h4' or self.hostname == 'h5':
                        client.server_hostname = self.ip_svrs[1]    #h7
                    elif self.hostname == 'h2':
                        client.server_hostname = self.ip_svrs[2]    #h8
                    elif self.hostname == 'h3':
                        client.server_hostname = self.ip_svrs[3]    #h9
                    
                    client.duration = 15
                    if j >= 5:
                        client.duration = 60
                    
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
                                filename = 'iperf3_total.txt'
                                with open(filename, "a") as file1:
                                    # Writing data to a file
                                    file1.write(json.dumps(json_test)+'\n')
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
    

#git clone https://github.com/Enrico-git/NGI-support.git
#sudo rm -rf /NGI-support-main/ ; sudo mv NGI-support/ /NGI-support-main
#python3 /NGI-support-main/config_host_static.py train 2 h0 192.168.0.2,192.168.0.4,192.168.0.9,192.168.0.11,192.168.0.15,192.168.0.17,192.168.0.30,192.168.0.32,192.168.0.37,192.168.0.39
#python3 /NGI-support-main/config_host_static.py test 15 h0 192.168.0.2,192.168.0.4,192.168.0.9,192.168.0.11,192.168.0.15,192.168.0.17,192.168.0.30,192.168.0.32,192.168.0.37,192.168.0.39
