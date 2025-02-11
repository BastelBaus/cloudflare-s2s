#!/bin/bash

# exit when any command fails
#set -e

printf "\n---------------------------------------------"
printf "Starting entry into container"
printf "Image built: $(cat /build-date.txt)"

printf "\n---------------------------------------------"
printf "Setting up warp"

##############################################
# setting up the cloudflare tunnel
##############################################

# create a tun device if not exist
# allow passing device to ensure compatibility with Podman
if [ ! -e /dev/net/tun ]; then
    mkdir -p /dev/net
    mknod /dev/net/tun c 10 200
    chmod 600 /dev/net/tun
fi

# start dbus
mkdir -p /run/dbus
if [ -f /run/dbus/pid ]; then
    rm /run/dbus/pid
fi
dbus-daemon --config-file=/usr/share/dbus-1/system.conf

# start the daemon
warp-svc --accept-tos > /warp-svc.log &

# sleep to wait for the daemon to start, default 2 seconds
sleep "$WARP_SLEEP"

# to this top accept the terms & conditions
# since --accept-tos does nto work reliable
#echo "y" | warp-cli status 
warp-cli --accept-tos status &

##############################################
# setting up the wireguad tunnel
##############################################

printf "\n---------------------------------------------"
printf "Setting up wireguard"

#ip link add dev wg0 type wireguard
#ip address add dev wg0 $CDIR_WG
#wg setconf wg0 /var/app/wg.conf
#ip link set up dev wg0

ip link add dev wg0 type wireguard
ip address add dev wg0 192.168.0.24/32
wg setconf wg0 /var/app/wg.conf
ip link set up dev wg0

##############################################
# setting api-server and WebUI-server
##############################################

printf "\n---------------------------------------------"
printf "starting the backend and frontend servers"


export FLASK_APP=/var/app/server/main.py 
echo   ${FLASK_APP}
python -m flask run -p $API_PORT &
python /var/app/client/main.py &

#flask --app ./server/main run -p $API_PORT &
#flask --app ./client/main run -p $WEBUI_PORT &

printf "\n---------------------------------------------"
printf "initialization finished:"
printf " API at port localhost:$API_PORT"
printf " WebUI at port localhost:$WEBUI_PORT"

##############################################
# done, sleep until forever
##############################################

sleep infinity
