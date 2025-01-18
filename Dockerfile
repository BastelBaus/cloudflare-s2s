# syntax=docker/dockerfile:1

#FROM docker.io/library/debian:bookworm-slim
FROM python:3.13-slim-bookworm

ENV WARP_SLEEP=2
ENV WEBUI_PORT=15650
ENV API_PORT=15651

#ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV TUNNEL_TOKEN=${TUNNEL_TOKEN:-""}


#ENV VERSION=$CLOUDFLARED_VERSION

# General settings
USER root
WORKDIR /var/app

# copy application and entry point data
COPY ./app .
COPY ./entrypoint.sh  .

# the volume to store the wireguad configuration
VOLUME /var/data/wireguard/ 
    # do we realy need this exposed ?
# what about cloudflare keys and so on ?


# install general packages
RUN apt-get update
RUN </dev/null DEBIAN_FRONTEND=noninteractive
RUN apt-get --yes install --no-install-recommends  \
        curl gpg ca-certificates dbus \
        cron tcpdump iputils-ping procps \ 
        wireguard \
        cargo                    

# install cloudflare-warp client
RUN /usr/bin/curl https://pkg.cloudflareclient.com/pubkey.gpg 
RUN /usr/bin/curl https://pkg.cloudflareclient.com/pubkey.gpg | gpg --yes --dearmor --output /usr/share/keyrings/cloudflare-warp-archive-keyring.gpg 
RUN echo "deb [arch=amd64 signed-by=/usr/share/keyrings/cloudflare-warp-archive-keyring.gpg] https://pkg.cloudflareclient.com/ bookworm main" | tee /etc/apt/sources.list.d/cloudflare-client.list 
RUN apt-get update &&  apt-get --yes install cloudflare-warp 
# clean the install
RUN apt-get clean
RUN rm -rf /var/lib/apt/lists/*

# setting up the python environment
#RUN pip install -r /var/app/requirements.txt
RUN pip install -r ./requirements.txt


EXPOSE ${WEBUI_PORT}
EXPOSE ${API_PORT}

#CMD ["flask", "--app", "./server/main", "run","-p", "5000"]
#CMD ["echo", "Docker setup finished"]
# calling the entrypoint which starts the server and the client
ENTRYPOINT ["./entrypoint.sh"]
