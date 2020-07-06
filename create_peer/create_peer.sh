#* * * * *   root    flock -xn /tmp/create_peer_ip -c 'cd /data/create_peer && ./create_peer.sh ip'
set -e
#source /mnt/sda3/root/python/anaconda3/etc/profile.d/conda.sh
#conda activate /mnt/sda3/root/python/lianjia-spider
#python create_peer.py ip
#scp ./ip.conf root@www.tandeen.com:/root/peers.conf
source /root/anaconda3/etc/profile.d/conda.sh
conda activate /root/python_env/creat_peer
python create_peer.py $1
cp ./$1.conf /root/$1.conf
#service squid restart
