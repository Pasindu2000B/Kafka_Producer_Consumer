# python producer/producer.py

from confluent_kafka import SerializingProducer
from confluent_kafka.serialization import StringSerializer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer
import random
import time

# Load Avro schema
with open('schema/order.avsc', 'r') as f:
    schema_str = f.read()

# Schema Registry configuration
schema_registry_conf = {'url': 'http://localhost:8082'}
schema_registry_client = SchemaRegistryClient(schema_registry_conf)

# Avro Serializer
avro_serializer = AvroSerializer(schema_registry_client, schema_str)

# Producer configuration
producer_conf = {
    'bootstrap.servers': 'localhost:9092',
    'key.serializer': StringSerializer('utf_8'),
    'value.serializer': avro_serializer
}

producer = SerializingProducer(producer_conf)

def delivery_report(err, msg):
    if err:
        print(f'✗ Delivery failed: {err}')
    else:
        print(f'✓ Message delivered to {msg.topic()} [{msg.partition()}]')

# Produce messages
products = ['Item1', 'Item2', 'Item3', 'Item4', 'Item5']
order_id = 1001

print("=== Order Producer Started ===\n")

try:
    while True:
        # 80% normal prices, 20% low prices (to trigger retries/DLQ)
        if random.random() < 0.8:
            price = round(random.uniform(30.0, 100.0), 2)
        else:
            price = round(random.uniform(10.0, 25.0), 2)
        
        order = {
            'orderId': str(order_id),
            'product': random.choice(products),
            'price': price
        }
        
        producer.produce(
            topic='orders',
            key=str(order_id),
            value=order,
            on_delivery=delivery_report
        )
        
        producer.poll(0)
        print(f'Produced: OrderID={order["orderId"]}, Product={order["product"]}, Price=${order["price"]:.2f}\n')
        
        order_id += 1
        time.sleep(2)
        
except KeyboardInterrupt:
    print('\n=== Producer Stopped ===')
finally:
    producer.flush()







