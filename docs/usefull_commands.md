
set a route to teh subnet in your router !

Note: cannot access teh host itself !!


tcpdump 

docker run -it --entrypoint /bin/bash
docker exec -it <mycontainer> sh

Listen on all interfaces for ping (icmp) commands
>> sudo tcpdump icmp -ni any

# routing
https://wiki.nftables.org/wiki-nftables/index.php/Ruleset_debug/tracing

 nft monitor trace


 sudo ip route add 192.168.1.0/24 via 192.168.0.23


connect 
https://stackoverflow.com/questions/44048915/unable-to-access-docker-containers-from-host-over-macvlan-network

https://blog.oddbit.com/post/2018-03-12-using-docker-macvlan-networks/


ip link add cf-s2s link eth0 type macvlan mode bridge
ip addr add 192.168.0.24/32 dev cf-s2s
ip link set cf-s2s up
ip route add 192.168.0.228/32 dev cf-s2s