### This project designed to secure data-sensitive IoT system for home environment
   Elements: 
#### 1- Secure MQTT broker using port 8883 act as message broker
   ##### Receives data from  a publisher
   ##### Subscriber subscrices to use a published data
#### 2- Publishers (IoT sensor devices):
   ##### Authenticate with MQTT using mTLS 
   ##### Publish IoT data
#### 3- Subscriber (Gateway) 
   ##### gateway subscribes into MQTT broker using mTLS
   ##### validate data according to predifined schema
   ##### minimize data
   ##### store data to encrypted Database
#### 4- encrypted database
   ##### stores data from subscriber
#### 5- Grafana as visualization tool 

