
** EARLY DEVELOPEMENT PHASE - NOT WORKING **

# What is it ?

cloudflare-s2s is a dockerized setup with web UI to open a cloudflare warp 
tunnel and set up a wirguard VPN through this tunnel. 
The resulting key benefits are:

* No IP or ports exposed due to cloudflare warp tunnel
* Full privacy with wireguard tunnel in tunnel (not visible for cloudflare)
* Easy web UI management of multi site tunnels and users 
* Includes network address translation to cope with same subnets (NAT)
* Dockerized application with only minor 

# Limitations

* the server work only on linux since on windows there is no macvlan supported. However you could still connect from a windows warp client to the network

# How it works 

# How to use it


# What is not implements

* only one subnet can be mapped
* only IPv4



https://www.procustodibus.com/blog/2021/11/wireguard-nftables/

https://www.procustodibus.com/blog/2020/12/wireguard-site-to-site-config/