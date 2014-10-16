# coding=utf8

import os
import sys
import time
import paho.mqtt.client as paho
import etcd
import json

g_sub_counter = 0
g_start_time = 0
g_end_time = 0

def on_connect(client, obj, rc):
    print("connection result: {0}".format(str(rc)))
    sys.stdout.flush()

def on_message(client, obj, mesg):
    global g_sub_counter
    global g_start_time
    global g_end_time

    g_sub_counter  += 1

    if g_sub_counter == 1:
        g_start_time = int(time.time()*1000)
        print("start time : {0} ms".format(g_start_time))
        sys.stdout.flush()

    if g_sub_counter == 100000:
        g_end_time = int(time.time()*1000)
        print("  end time : {0} ms".format(g_end_time))
        print("delta time : {0} ms".format(g_end_time - g_start_time))
        sys.stdout.flush()

    #print("mesg: {0} {1} {2} {3}".format(mesg.topic, str(mesg.qos), str(mesg.payload), str(g_sub_counter)))
    #sys.stdout.flush()

def on_publish(client, obj, mid):
    print("Published mid: {0}".format(str(mid)))
    sys.stdout.flush()

def on_subscribe(client, obj, mid, granted_qos):
    print("Subscribed: "+str(mid)+" "+str(granted_qos))
    sys.stdout.flush()

def on_log(client, obj, level, string):
    print(string)
    sys.stdout.flush()

if __name__ == '__main__':
    try:
        #etcd_client = etcd.Client(host='172.17.42.1')
        #etcd_client = etcd.Client(host='10.1.42.1')
        etcd_addr = os.environ.get('ETCD_SERVER_ADDR') or "127.0.0.1"
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
    client.on_subscribe = on_subscribe

    try:
        client.connect(mqtt_server_addr, 1883, 60)
        client.subscribe("my/topic/string", 0)
        client.loop_forever()
    except:
        print("MQTT server: connection refused")
        sys.stdout.flush()
