# syntax=docker/dockerfile:1.2

#FROM docker.io/library/debian:bookworm-slim
FROM python:3.13-slim-bookworm
#FROM alpine:3.21

ENV WARP_SLEEP=2
ENV FLASK_RUN_HOST=0.0.0.0

ENV WEBUI_PORT=${WEBUI_TOKEN:-"15650"}
ENV API_PORT=${API_TOKEN:-"15651"}

#ENV FLASK_APP=app.py
ENV TUNNEL_TOKEN=${TUNNEL_TOKEN:-""}
ENV SERVER_NAME=${SERVER_NAME:-""}
ENV AUTO_CONNECT=${AUTO_CONNECT:-"1"}
ENV CDIR_WG=192.168.242.1/24
    

RUN date >/build-date.txt

#ENV VERSION=$CLOUDFLARED_VERSION

# General settings
USER root
WORKDIR /var/app

# the volume to store the wireguad configuration
VOLUME /var/data


# install general packages
RUN apt-get update
RUN </dev/null DEBIAN_FRONTEND=noninteractive
#RUN apt-get --yes install --no-install-recommends cargo                    

# install some tools for net monitoring
RUN apt-get --yes install --no-install-recommends \
     curl cron tcpdump iputils-ping procps telnet mtr nmap

# install wireguard
RUN apt-get --yes install --no-install-recommends  wireguard


# Install cloudflare 
RUN apt-get --yes install --no-install-recommends gpg ca-certificates dbus 
RUN apt-get --yes install --no-install-recommends lsb-release         
RUN curl -fsSL https://pkg.cloudflareclient.com/pubkey.gpg | gpg --yes --dearmor --output /usr/share/keyrings/cloudflare-warp-archive-keyring.gpg
RUN echo "deb [signed-by=/usr/share/keyrings/cloudflare-warp-archive-keyring.gpg] https://pkg.cloudflareclient.com/ $(lsb_release -cs) main" | tee /etc/apt/sources.list.d/cloudflare-client.list
RUN apt-get update && apt-get install -y cloudflare-warp

# clean the install
RUN apt-get clean
RUN rm -rf /var/lib/apt/lists/*

# setting up the python environment
COPY ./app/requirements.txt /var/app
RUN pip install -r ./requirements.txt

EXPOSE ${WEBUI_PORT}
EXPOSE ${API_PORT}

# copy application and entry point data
COPY ./app/frontend /var/app/frontend
COPY ./app/backend  /var/app/backend
COPY ./app/lib/*.py /var/app/lib
COPY ./app/*.py     /var/app/
COPY ./app/wg.conf  .
COPY --chmod=755 ./entrypoint.sh  .
#COPY ./entrypoint.sh  .
RUN ["chmod", "+x", "./entrypoint.sh"]

ENTRYPOINT ["./entrypoint.sh"]
