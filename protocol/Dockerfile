FROM resin/raspberrypi3-python

# Install dependencies
RUN apt-get update && apt-get install --no-install-recommends -y \
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
WORKDIR /usr/src/app 

COPY requirements.txt requirements.txt

RUN python3 -m pip install -r requirements.txt

COPY config config
COPY dbus_protocols dbus_protocols
COPY dbus_server.py dbus_server.py
COPY mqtt mqtt 
COPY utils utils 

CMD ./dbus_server.py