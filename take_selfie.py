#!/usr/bin/python
# Writen by Darian Johnson
# this was build leveraging Mario Cannistra's IoT project - https://www.hackster.io/mariocannistra/radio-astronomy-with-rtl-sdr-raspberrypi-and-amazon-aws-iot-45b617

# This python code runs on the raspberry pi and takes a selfie when a message is recieved from the Alexa skill
# this code is part of the Mystic Mirror Project 
# for questions, contact me on Twitter @DarianBJohnson


import paho.mqtt.client as paho
import os
import socket
import ssl
import uuid
import json
import tinys3

#update with the email address used when you linked the Mystic Mirror skill to your Google account
email = 'danieletatasciore@gmail.com'
s3_bucket = 'selfie-alexa1' #change this if you plan to use your own Alexa skill and IoT

def on_connect(client, userdata, flags, rc):
    print("Connection returned result: " + str(rc) )
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    # Subscribe to "test" topic only
    client.subscribe("selfie")

def on_message(client, userdata, msg):
    print("topic: "+msg.topic)
    print("payload: "+str(msg.payload))
    
    #Logic to take the selfie
    try:
        #delete old photos
        os.system("rm Photos/*.jpg")
        
        #take a photo using the name passed to us from mqtt message
        photo  = "Photos/" + str(msg.payload) + ".jpg"
        photo = photo.replace("/b'","/")
        photo = photo.replace("'","")
        photo = photo.replace("`","")
        os_string = "fswebcam --no-banner " + photo
        os.system(os_string)
        
        #publish a message letting the magic_mirror presentation layer know that the picture was taken. This is so that the picture can be displayed.
        message = 'success'
        payload = json.dumps({'intent':'selfie-taken','message': 'success' ,'photo': photo})
        mqttc.publish('display', payload, qos=1)
        print('published')
        
        #use tinyS3 to upload the photo to AWS S3
        #Note this key only allows write access to the mysticmirror bucket; contact Darian Johnson for the key for this access
        S3_SECRET_KEY = 'WEUKlD1qGWfibHSYj/6YCrgnfcN7MpHeyLG2S08U' 
        S3_ACCESS_KEY = 'AKIAICSJI4HPU7Q2YSKQ'
        
        conn = tinys3.Connection(S3_ACCESS_KEY,S3_SECRET_KEY,tls=True, endpoint='s3-us-west-2.amazonaws.com')
        f = open(photo,'rb')
        conn.upload(photo,f,s3_bucket)
        conn.get(photo,f,s3_bucket)
            
            
    except:
        payload = json.dumps({'intent':'selfie-taken','message':'error'})
        mqttc.publish('/display', payload, qos=1)
        message = 'error'
        print('did not publish')

mqttc = paho.Client()
mqttc.on_connect = on_connect
mqttc.on_message = on_message
#mqttc.on_log = on_log

#variables to connect to AWS IoT
#Note these certs allow access to send IoT messages; contact Darian Johnson for the certs (if you are building a mystic mirror and want to leverage his solution)
awshost = "awvqjuvfg8tl0.iot.us-west-2.amazonaws.com"
awsport = 8883
clientId = "mirror" + str(uuid.uuid4())
thingName = "mirror"

caPath = "/home/pi/cert/root-CA.crt" #SUCH AS "/home/pi/certs/verisign-cert.pem  "
certPath = "/home/pi/cert/mirror.cert.pem" #SUCH AS "/home/pi/certs/certificate.pem.crt"
keyPath = "/home/pi/cert/mirror.private.key" #SUCH AS "/home/pi/certs/private.pem.key"

# caPath = "/home/pi/3b69de4f3f-certificate.pem.crt"
# certPath = "verisign.pem"
# keyPath = "/home/pi/3b69de4f3f-private.pem.key"

# certPath = "/home/pi/3b69de4f3f-certificate.pem.crt"
# caPath = "verisign.pem"
# keyPath = "/home/pi/3b69de4f3f-private.pem.key"

mqttc.tls_set(caPath, certfile=certPath, keyfile=keyPath, cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLSv1_2, ciphers=None)

mqttc.connect(awshost, awsport, keepalive=60)

mqttc.loop_forever() 

# while 1==1:
#     sleep(0.5)
#     f = open('test')
#     imagine
    
