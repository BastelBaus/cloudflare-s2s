#!/bin/bash

# exit when any command fails
#set -e

echo ""
echo "---------------------------------------------"
echo "Starting entry into container: $SERVER_NAME"
echo "Image built: $(cat /build-date.txt)"

echo ""
echo "---------------------------------------------"
echo "Setting up warp"

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

echo ""
echo "---------------------------------------------"
echo "Setting up wireguard"

#ip link add dev wg0 type wireguard
#ip address add dev wg0 $CDIR_WG
#wg setconf wg0 /var/app/wg.conf
#ip link set up dev wg0

#ip link add dev wg0 type wireguard
#ip address add dev wg0 192.168.0.24/32
#wg setconf wg0 /var/app/wg.conf
#ip link set up dev wg0

##############################################
# adding up the outside route to host
##############################################

echo ""
echo "---------------------------------------------"
echo "allowing route to local host by routing      "
echo "  all traffic from inside to outside trough  "
echo "  the default interface and not the macvlan  "
ip route del ${SUBNET}

#old
#localip=$(hostname  -i | cut -f1 -d' ')
#ip route add via ${localip}

##############################################
# setting api-server and WebUI-server
##############################################

echo ""
echo "---------------------------------------------"
echo "starting the backend and frontend servers for $SERVER_NAME"


#export FLASK_APP=/var/app/main_backend.py 
#echo   ${FLASK_APP}
#python -m flask run -p $API_PORT &
python /var/app/main_backend.py &
python /var/app/main_frontend.py &

#flask --app ./server/main run -p $API_PORT &
#flask --app ./client/main run -p $WEBUI_PORT &

echo ""
echo "---------------------------------------------"
echo "initialization finished:"
echo " API at port localhost:$API_PORT"
echo " WebUI at port localhost:$WEBUI_PORT"
echo "---------------------------------------------"

##############################################
# done, sleep until forever
##############################################

sleep infinity
