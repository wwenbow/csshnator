#CSSHNATOR

cssh for terminator to manager a cluster of nodes through ssh connections
launches multiple splits with ssh connections to each node

##Requirements

Only for Terminator 0.98+

Ubuntu can get from this PPA
https://launchpad.net/~gnome-terminator/+archive/ubuntu/ppa

sudo apt-add-repository ppa:gnome-terminator/ppa

##Usage
Create a config file with all the clusters listed in
$HOME/.csshnatorrc

cluster1 = 10.10.100.209 10.10.100.210 10.10.100.211

Cluster name followed by space separated list of nodenames/IPs

run ccshnator -l <user> -c <clustername>
