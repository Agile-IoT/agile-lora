#################################################################
#   Copyright (C) 2018  
#   This program and the accompanying materials are made
#   available under the terms of the Eclipse Public License 2.0
#   which is available at https://www.eclipse.org/legal/epl-2.0/ 
#   SPDX-License-Identifier: EPL-2.0
#   Contributors: ATOS SPAIN S.A.
################################################################# 

# agile-lora installation
FROM resin/raspberrypi3-python
WORKDIR /usr/src/app 
ENV APATH /usr/src/app

# Add packages
RUN apt-get update && apt-get install --no-install-recommends -y \
    # openjdk-7-jdk \
    qdbus \  
    python3-dbus \
    libdbus-1-dev \
    libdbus-glib-1-dev \
    python3-gi \
    python3-pip \
    build-essential \
    python3-dev \
    python3-tk \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

COPY . .

RUN python3 -m pip install -r requirements.txt 
CMD [ "bash", "/usr/src/app/scripts/start.sh" ]