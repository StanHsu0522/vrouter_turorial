FROM ubuntu:16.04
MAINTAINER stan

WORKDIR /

RUN apt update && apt install -y \
    psmisc \
    ethtool \
    isc-dhcp-server \
    net-tools \
    iproute2 \
    iputils-ping \
    vim \
    zip \
    unzip \
    gawk \
    texinfo \
    python-pip \
    build-essential \
    iptables \
    automake \
    autoconf \
    libtool \
    git \
    sudo \
    mininet \
  && pip install -U pip && pip install ipaddress

# install quagga and enable fpm
RUN git clone -b onos-1.11 https://gerrit.opencord.org/quagga \
  && cd quagga/ \
  && ./bootstrap.sh \
  && ./configure --enable-fpm --sbindir=/usr/lib/quagga enable_user=root enable_group=root \
  && make \
  && make install \
  && cd ../ \
  && ldconfig \
  && mkdir /var/run/quagga/

RUN echo "service openvswitch-switch start\n" >> /root/.bashrc