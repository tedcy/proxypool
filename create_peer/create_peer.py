import pymysql
import requests
import time
import threadpool
import threading

import numpy as np

import sys
tablename = sys.argv[1]
sys.stdout = open('./create_peer_' + tablename + '.log', "a")

used_time_list = []
valid_list = []
valid_count = 0
total_count = 0
mutex = threading.Lock()
def stats_result():
    global used_time_list
    global valid_count
    global total_count
    if not used_time_list or not total_count:
        return
    used_time_array = np.asarray(used_time_list, np.float32)
    print('Total Count:', total_count,
          'Valid Count:', valid_count,
          'Valid Percent: %.2f%%' % (valid_count * 100.0 / total_count),
          'Used Time Mean:', used_time_array.mean(),
          'Used Time Var', used_time_array.var())
    sys.stdout.flush()   

def threadpool_callback(workWorkRequest, result):
    global valid_count
    global total_count
    addr = result[0]
    ok = result[1]
    ms = result[2]
    mutex.acquire()
    if ok:
        print(addr, ms)
        sys.stdout.flush()
        valid_count += 1
        used_time_list.append(ms)
        valid_list.append(addr)
    total_count += 1
    mutex.release()

test_url = 'http://c.tieba.baidu.com/'
timeout = 20

def testproxyonce(addr):
    try:
        proxies = {
            'http': addr,
        }
        start_time = time.time()
        r = requests.get(test_url, timeout=timeout, proxies=proxies)
        if len(r.content) < 5000:
            return False, None
        end_time = time.time()
        used_time = end_time - start_time
        return True, used_time
    #except (ProxyError, ConnectTimeout, SSLError, ReadTimeout, ConnectionError):
    except KeyboardInterrupt as e:
        raise KeyboardInterrupt
    except Exception as e:
        #print('Proxy Invalid:', addr, e, e.__traceback__.tb_lineno)
        #sys.stdout.flush()
        return False, None

def testproxy(addr):
    count = 2
    sum_time = 0
    ok_count = 0
    resultOk = True
    for i in [count]:
        ok, ms = testproxyonce(addr)
        if ok:
            sum_time += ms
            ok_count += 1
        else:
            resultOk = False
    mean_time = 0
    if ok_count:
        mean_time = sum_time / ok_count
    if mean_time > 3:
        resultOk = False
    return addr, resultOk, mean_time

try:
    pool_size = 100
    pool = threadpool.ThreadPool(pool_size)
    print('-----------------start------------------')
    sys.stdout.flush()
    conn = pymysql.connect(
        host='127.0.0.1',
        user = '',
        password = '',
        db = 'ProxyPool',
        charset = 'utf8'
    )

    cursor = conn.cursor()
    cursor.execute('select * from ' + tablename + ' order by id desc limit 1000')
    results = cursor.fetchall()

    addr_list = []
    for row in results:
        addr_list.append(row[1])

    rs = threadpool.makeRequests(testproxy, addr_list, threadpool_callback)

    [pool.putRequest(req) for req in rs]
    pool.wait()
    pool.dismissWorkers(pool_size, do_join=True)
    
    stats_result()
     
    if len(valid_list) == 0:
        raise(Exception('wtf'))
    filename = tablename + '.conf'
    with open(filename, 'w') as file_object:
        for u in valid_list:
            addr = u.split(':')
            ip = addr[0]
            port = addr[1]
            file_object.write('cache_peer ')
            file_object.write(ip)
            file_object.write(' parent ')
            file_object.write(port)
            file_object.write(' 0 no-query no-digest weighted-round-robin weight=1 connect-fail-limit=1 allow-miss\n')
    print('-----------------end------------------')
    sys.stdout.flush()
except Exception as e:
    print(e, e.__traceback__.tb_lineno)
    sys.stdout.flush()
    print('-----------------end------------------')
