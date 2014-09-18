# coding=utf8

import os
from time import sleep
import paho.mqtt.client as paho
import etcd
import json

def on_connect(client, obj, rc):
    print("connection result: {0}".format(str(rc)))

def on_message(client, obj, mesg):
    print("mesg: {0} {1} {2}".format(mesg.topic, str(mesg.qos), str(mesg.payload)))

def on_publish(client, obj, mid):
    print("Published mid: {0}".format(str(mid)))

def on_log(client, obj, level, string):
    print(string)

if __name__ == '__main__':
    try:
        #client = etcd.Client(host='172.17.42.1')
        client = etcd.Client(host='10.1.42.1')
        mqtt_server = json.loads(client.read('/services/mqtt-broker').value)
        mqtt_server_addr = mqtt_server["ipaddr"]
    except:
        mqtt_server_addr = os.environ.get('MQTT_SERVER_ADDR') or "127.0.0.1"

    print("MQTT server: " + mqtt_server_addr)

    client = paho.Client()
    client.on_message = on_message
    client.on_connect = on_connect
    client.on_publish = on_publish

    try:
        client.connect(mqtt_server_addr, 1883, 60)

        i = 0
        while client.loop() == 0:
            client.publish("my/topic/string", "hello%d"%i, qos=0)
            if i == 10000:
                break
            else:
                i+=1
                sleep(1)
            pass
    except:
        print("MQTT server: connection refused")
