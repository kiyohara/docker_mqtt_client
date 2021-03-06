# coding=utf8

import os
import sys
import time
from time import sleep
import paho.mqtt.client as paho
import etcd
import json

PUBLISH_CNT = 1000000
PUB_PER_SEC = 6100

g_pub_counter = 0
g_start_time = 0
g_end_time = 0

def on_connect(client, obj, rc):
    print("connection result: {0}".format(str(rc)))
    sys.stdout.flush()

def on_message(client, obj, mesg):
    print("mesg: {0} {1} {2}".format(mesg.topic, str(mesg.qos), str(mesg.payload)))
    sys.stdout.flush()

def on_publish(client, obj, mid):
    global g_pub_counter
    global g_start_time
    global g_end_time

    g_pub_counter += 1

    if g_pub_counter == 1:
        g_start_time = int(time.time()*1000)
        print("start time : {0} ms".format(g_start_time))
        sys.stdout.flush()

    if g_pub_counter == PUBLISH_CNT:
        g_end_time = int(time.time()*1000)
        print("  end time : {0} ms".format(g_end_time))
        print("delta time : {0} ms".format(g_end_time - g_start_time))
        sys.stdout.flush()

    # print("Published mid: {0}".format(str(mid)))
    # sys.stdout.flush()

def on_log(client, obj, level, string):
    print(string)
    sys.stdout.flush()

if __name__ == '__main__':
    try:
        #etcd_client = etcd.Client(host='172.17.42.1')
        #etcd_client = etcd.Client(host='10.1.42.1')
        etcd_addr = os.environ.get('ETCD_SERVER_ADDR') or "127.0.0.1"
        etcd_client = etcd.Client(host=etcd_addr)
        print("etcd server: " + etcd_addr)
        sys.stdout.flush()
        etcd_client = etcd.Client(host=etcd_addr)

        mqtt_server = json.loads(etcd_client.read('/services/mqtt-broker', timeout=1).value)
        mqtt_server_addr = mqtt_server["ipaddr"]
    except:
        print("etcd server: connection refused")
        mqtt_server_addr = os.environ.get('MQTT_SERVER_ADDR') or "127.0.0.1"

    print("MQTT server: " + mqtt_server_addr)
    sys.stdout.flush()

    client = paho.Client()
    client.on_message = on_message
    client.on_connect = on_connect
    client.on_publish = on_publish

    try:
        client.connect(mqtt_server_addr, 1883, 60)

        pub_interval = 1 / PUB_PER_SEC
        print("pub interval: {0}".format(pub_interval))

        i = 1
        start_time = time.time()
        while client.loop() == 0:
            client.publish("my/topic/string", "hello%d"%i, qos=0)

            if i == PUBLISH_CNT:
                break
            else:
                next_pub_time = start_time + (i * pub_interval)
                #print("next pubt : {0}".format(next_pub_time))

                crr_time = time.time()
                #print("crr time  : {0}".format(crr_time))

                sleep_time = next_pub_time - crr_time
                #print("sleep time : {0}".format(sleep_time))

                if sleep_time > 0:
                    sleep(sleep_time)

                i+=1
            pass
    except:
        print("MQTT server: connection refused")
        sys.stdout.flush()
