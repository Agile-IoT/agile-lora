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

RUN sudo DBUS_SESSION_BUS_ADDRESS=unix:path=/usr/src/app/.agile_bus/agile_bus_socket ./dbus_server.py
