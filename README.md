# NGI-support

This is the structure of the NGI-support public repository:
```
├── config_docker.sh
├── config_host.py
├── config_host_static.py
├── config_host_static_max.py
├── config_host_static_one.py
├── config_host_static_subprocess.py
└── config_ovs.sh
```

Let's analyze step by step what each directory contains.
- ``` config_docker.sh ``` donwload docker engine; download pull; create docker container.
- ``` config_host.py ```  generates randomically traffic to all hosts. Used in 4SW experiment.
- ``` config_host_static.py ```  generates statically traffic to target hosts. Used in 8SW experiment.
- ``` config_host_static_max.py ```  generates statically traffic to target hosts. Used in 8SW experiment. Every hosts send the maximum bandwidth.
- ``` config_host_static_subprocess.py ```  generates statically traffic to target hosts. Used in 8SW experiment. uses subprocess instead of iperf3 python library.
- ``` config_ovs.sh ``` map the switch port with the OVS port.
-----
