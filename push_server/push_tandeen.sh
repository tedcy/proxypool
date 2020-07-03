set -e
set -x
go build ..
cp ../proxypool proxypool
ssh www.tandeen.com "mkdir -pv /data/proxypool/conf"
scp proxypool root@www.tandeen.com:/data/proxypool/main
scp ../conf/app.ini root@www.tandeen.com:/data/proxypool/conf
scp *.sh root@www.tandeen.com:/data/proxypool/
scp create.sql root@www.tandeen.com:/data/proxypool/
