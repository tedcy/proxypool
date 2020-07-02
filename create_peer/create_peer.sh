source /mnt/sda3/root/python/anaconda3/etc/profile.d/conda.sh
conda activate /mnt/sda3/root/python/lianjia-spider
python create_peer.py 2>&1 >> create_peer.log
scp ./peers.conf root@47.99.219.218:/root/peers.conf
