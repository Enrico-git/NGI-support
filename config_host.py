import sys
import random
import subprocess
import time

class TrafficGenerator:

    def __init__(self):
       self.hostname=sys.argv[1]
       self.list_ip=sys.argv[2].split(',')
       
       self.svr_num = int(len(list_ip)/3)
       
       proc = subprocess.run(['hostname', '-I'], capture_output=True)
       list_addresses = proc.stdout.decode('utf-8').split(' ')
       self.my_addr = list(filter(lambda el: el.startswith('192.168'), list_addresses))[0]
       
 #       self.hosts = {x: f'192.168.1.{x}' for x in range(3, 5)}

        self.iperf_time = 60    # seconds
        self.num_iperf = 60*10  # 1 min * 10 = 10 min * 6 = 1 h * 6 = 6h
        random.seed(19951018+int(self.hostname[1:]))    

    def generate_traffic(self):    
        if self.my_addr in self.list_ip[-self.svr_num:]: #one of the server
            print(f'iperf3 -s from {self.my_addr}')
            subprocess.run(['iperf3', '-s'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        for i in range(self.num_iperf):
            print(f'iteration {i}/{self.num_iperf}')
            if self.hostname != 'h0':
                # generate a random iperf3 request: f(t, bw, svr)
                r_index = -random.randint(1, self.svr_num)   #-1, -2, -N
                client = self.list_ip[r_index]  # NOTE: last addresses in the list are used as iperf3 -s
                bw = random.randint(1, 10)
                iperf_time = random.randint(30, 90)
            else:
                #the first host does static request to the last server only
                client = self.list_ip[-1]
                bw = 10
                iperf_time = 120
            print(f'iperf to {client}, bw: {bw}, time: {iperf_time}')
            subprocess.run(['iperf3', '-c', client, '-b', f'{bw}M', '-t', f'{iperf_time}'],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(random.randint(1, 10))
                
                
                


if __name__ == '__main__':
    tf = TrafficGenerator()
#    tf.generate_traffic()
