from __future__ import print_function

import json
import boto3
from kafka import KafkaProducer
import urllib
import ssl
import logging

root = logging.getLogger()
if root.handlers:
    for handler in root.handlers:
        root.removeHandler(handler)
logging.basicConfig(format='%(asctime)s %(message)s',level=logging.DEBUG)

print('Loading function')

s3 = boto3.client('s3')

context = ssl.create_default_context()
context.options &= ssl.OP_NO_TLSv1
context.options &= ssl.OP_NO_TLSv1_1

producer = KafkaProducer(
   bootstrap_servers=['pkc-loyje.us-central1.gcp.confluent.cloud:9092'],
   value_serializer=lambda m: json.dumps(m).encode('ascii'),
   retry_backoff_ms=500,
   request_timeout_ms=20000,
   security_protocol='SASL_SSL',
   sasl_mechanism='PLAIN',
   ssl_context=context,
   sasl_plain_username='KAQ6FBDAGJHXTNUD',
   sasl_plain_password='+Vz/bZr89unWz8f2ufuDUeJgKSB2/BBFtAsxgCM6cstG2WrO6cK4lMTfoTyewSUv')



def lambda_handler(event, context):
        
    print("Received event: " + json.dumps(event, indent=2))

    # Get the object from the event and show its content type
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.unquote_plus(event['Records'][0]['s3']['object']['key'].encode('utf8'))
    try:
        print("We have new object. In bucket {}, with key {}".format(bucket, key))
        future = producer.send("webapp","We have new object. In bucket {}, with key {}".format(bucket, key))
        record_metadata = future.get(timeout=10)
        print("sent event to Kafka! topic {} partition {} offset {}".format(record_metadata.topic, record_metadata.partition, record_metadata.offset))

    except Exception as e:
        print(e)
        print('Error getting object {} from bucket {}. Make sure they exist and your bucket is in the same region as this function.'.format(key, bucket))
        raise e


