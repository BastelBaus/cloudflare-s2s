# syntax=docker/dockerfile:1

#FROM docker.io/library/debian:bookworm-slim
FROM python:3.13-slim-bookworm
#FROM alpine:3.21

ENV WARP_SLEEP=2
ENV WEBUI_PORT=15650
ENV API_PORT=15651

#ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV TUNNEL_TOKEN=${TUNNEL_TOKEN:-""}
ENV CDIR_WG=192.168.242.1/24

RUN date +%Y%m%d > /build-date.txt

#ENV VERSION=$CLOUDFLARED_VERSION

# General settings
USER root
WORKDIR /var/app

# copy application and entry point data
COPY ./app .
COPY --chmod=755 ./entrypoint.sh  .
RUN ["chmod", "+x", "./entrypoint.sh"]


# the volume to store the wireguad configuration
VOLUME /var/data/wireguard/ 
    # do we realy need this exposed ?
# what about cloudflare keys and so on ?


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
#RUN pip install -r /var/app/requirements.txt
RUN pip install -r ./requirements.txt


EXPOSE ${WEBUI_PORT}
EXPOSE ${API_PORT}

RUN date >/build-date.txt

#CMD ["flask", "--app", "./server/main", "run","-p", "5000"]
#CMD ["echo", "Docker setup finished"]
# calling the entrypoint which starts the server and the client
ENTRYPOINT ["./entrypoint.sh"]
