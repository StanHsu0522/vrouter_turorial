# Virtual Router (vRouter) Tutorial

The environment is already set up in the docker image. In this tutorial, we utilize `Docker`, `ONOS`, `OVS`, `Mininet`, `Quagga`.  



## Prerequisite

Install ONOS  
Install `Docker` and add LOGIN_USER into docker group

```bash
    sudo apt update && apt install docker.io
    sudo usermod -aG docker LOGIN_USER
```

Pull the docker image

```bash
    docker pull stanhsu0522/onos_vrouter
```



## How to Start

### VROUTER

1. Start the container

    Use option '-v' (volume) to map directory between host and container

```bash 
    docker run -it --privileged -v 'HOST_DIR':'CONTAINER_DIR' stanhsu0522/onos_vrouter
    # docker run -it --privileged -v ~/onos_vrouter:/onos_vrouter stanhsu0522/onos_vrouter
```

2. Start ONOS and setup

    Activate `vrouter` app  
    Feed network configurations (`/config/network-cfg.json`) to ONOS

```bash
    onos localhost app activate vrouter
    onos-netcfg localhost 'HOST_DIR'/VROUTER/config/network-cfg.json
```

3. Start Mininet (Inside container)

    Fill up the correct IP for ONOS instant

```bash
   root@container:/ cd 'HOST_DIR'/VROUTER/
   root@container:/ ./launcher 'ONOS_INSTANT_IP'        # ./launcher 192.168.0.1
```

4. Test connectivity in Mininet

    Do NOT test connectivity until routing info is correct and flow rules are installed

```bash
    mininet> h1 ping h3 -c 3
```

*Note: Remember to clean up Mininet after each experiment.*



### TRELLIS

1. Start the container

    Use option '-v' (volume) to map directory between host and container

```bash 
    docker run -it --privileged -v 'HOST_DIR':'CONTAINER_DIR' stanhsu0522/onos_vrouter
    # docker run -it --privileged -v ~/onos_vrouter:/onos_vrouter stanhsu0522/onos_vrouter
```

2. Start ONOS and setup

    Activate `drivers`, `openflow`, `segmentrouting`, `fpm`, `dhcprelay`, `netcfghostprovider`, `routeradvertisement`, `mcast ` apps  
    Feed network configurations (`trellisV4.json`) to ONOS

```bash
    onos localhost app activate drivers org.onosproject.openflow segmentrouting fpm dhcprelay netcfghostprovider routeradvertisement mcast
    onos-netcfg localhost 'HOST_DIR'/TRELLIS/routing/trellis/trellisV4.json
```

3. Start Mininet (Inside container)

    Fill up the correct IP for ONOS instant

```bash
   root@container:/ cd 'HOST_DIR'/TRELLIS/routing/trellis/
   root@container:/ ./trellisV4.py --controllers 'ONOS_INSTANT_IP' ...        # ./trellisV4.py --controllers 192.168.0.1
```

4. Test connectivity in Mininet

    * Do NOT test connectivity until routing info is correct and flow rules are installed
    * Two hosts under each leaf switch (i.e. h1–h4)
    * One DHCP server 
    * One internal Quagga speaker at s205
    * One exteral Quagga speaker (metro router)
    * One remote host behind external router (i.e. rh1)

```bash
    mininet> h1 ping h3 -c 3
    mininet> h1 ping rh1 -c 3
```

*Note: Remember to clean up Mininet after each experiment.*



## Trouble shooting

* ONOS netcfg check
    ```bash
        onos localhost netcfg
    ```
* Quagga FIB push interface check
    ```bash
        mininet> ospfbgp ping 'ONOS_INSTANT_IP'
    ```
* Quagga daemon check 
    ```bash
        mininet> r1 /quagga/zebra/zebra -d -f configs/zebra.conf -z /var/run/quagga/zebrar1.api -i /var/run/quagga/zebrar1.pid
        mininet> r1 /quagga/ospfd/ospfd -d -f configs/quagga1.conf -z /var/run/quagga/zebrar1.api -i /var/run/quagga/ospfdr1.pid
    ```
* BGP speaker route check  
    *note: It takes time for forwarding info to calculate.*
    ```bash
        mininet> ospfbgp ip route
    ```
* ONOS route check
    ```bash
        onos localhost routes
    ```
* DHCP IP allocation check 
    ```bash
        mininet> h1 ip addr 
    ```
* Clean up mininet
    ```bash
        mn -c
    ```



## Reference
[ONOS vRouter](https://wiki.onosproject.org/display/ONOS/vRouter)
