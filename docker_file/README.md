# ONOS Vouter  

## Pull necessary files  

Please pull files from github first.

```bash
    git clone https://github.com/StanHsu0522/onos_vrouter.git
```

## Usage  

Remamber to map directory between host and container by volumes (-v).

```bash
    docker run -it --privileged -v 'HOST_DIR':'CONTAINER_DIR' stanhsu0522/onos_vrouter
```

## Components  

This image contains:  
* `Mininet 2.2.1`  
* `OpenVSwitch 2.5.5`  
* `Quagga`  
