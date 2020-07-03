set -e
set -x

ssh www.tandeen.com "mkdir -pv /data/create_peer"
scp create_peer.py root@www.tandeen.com:/data/create_peer/
