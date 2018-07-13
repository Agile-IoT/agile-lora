#################################################################
#   Copyright (C) 2018  
#   This program and the accompanying materials are made
#   available under the terms of the Eclipse Public License 2.0
#   which is available at https://www.eclipse.org/legal/epl-2.0/ 
#   SPDX-License-Identifier: EPL-2.0
#   Contributors: ATOS SPAIN S.A.
################################################################# 

#AGILE DBUS JAVA INTERFACE installation/connection

ARG BASEIMAGE_BUILD=agileiot/raspberry-pi3-zulujdk:8-jdk-maven
ARG BASEIMAGE_DEPLOY=agileiot/raspberry-pi3-zulujdk:8-jre

FROM $BASEIMAGE_BUILD

# Add packages
RUN apt-get update && apt-get install --no-install-recommends -y \
    build-essential \
    git\
    ca-certificates \
    apt \
    software-properties-common \
    unzip \
    cpp \
    binutils \
    maven \
    gettext \
    libc6-dev \
    make \
    cmake \
    cmake-data \
    pkg-config \
    clang \
    gcc-4.9 \
    g++-4.9 \
    qdbus \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# resin-sync will always sync to /usr/src/app, so code needs to be here.
WORKDIR /usr/src/app
ENV APATH /usr/src/app

COPY scripts scripts

COPY agile-dbus-java-interface agile-dbus-java-interface
RUN CC=clang CXX=clang++ CMAKE_C_COMPILER=clang CMAKE_CXX_COMPILER=clang++ \
scripts/install-agile-interfaces.sh $APATH/deps

# agile-lora installation
# FROM ubuntu:18.04
FROM resin/raspberrypi3-python

# Install dependencies
RUN apt-get update && apt-get install --no-install-recommends -y \ 
  apt-utils \  
  python3-dbus \
  libdbus-1-dev \
  libdbus-glib-1-dev \
  python3-gi \
  python3-pip \
  build-essential \
  python3-dev \
  python3-tk \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# resin-sync will always sync to /usr/src/app, so code needs to be here.
COPY . /usr/src/app 
WORKDIR /usr/src/app 
RUN python3 -m pip install -r requirements.txt 

# ENV DBUS_SESSION_BUS_ADDRESS=unix:path=/usr/src/app/.agile_bus/agile_bus_socket
# RUN sudo DBUS_SESSION_BUS_ADDRESS=unix:path=/usr/src/app/.agile_bus/agile_bus_socket ./dbus_server.py


CMD [ "bash", "/usr/src/app/scripts/start.sh" ]