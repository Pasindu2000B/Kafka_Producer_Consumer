
from confluent_kafka import DeserializingConsumer, Consumer, Producer
from confluent_kafka.serialization import StringDeserializer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroDeserializer
import time
import json

# Schema Registry configuration
schema_registry_conf = {'url': 'http://localhost:8082'}
schema_registry_client = SchemaRegistryClient(schema_registry_conf)

# Avro Deserializer
avro_deserializer = AvroDeserializer(schema_registry_client)

# Main consumer (Avro) for 'orders' topic
consumer_conf_avro = {
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'order-consumer-group',
    'auto.offset.reset': 'earliest',
    'enable.auto.commit': True,
    'auto.commit.interval.ms': 1000,
    'key.deserializer': StringDeserializer('utf_8'),
    'value.deserializer': avro_deserializer
}

# Retry consumer (Plain String) for 'orders-retry' topic
consumer_conf_retry = {
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'order-consumer-group',
    'auto.offset.reset': 'earliest',
    'enable.auto.commit': True,
    'auto.commit.interval.ms': 1000,
}

consumer_avro = DeserializingConsumer(consumer_conf_avro)
consumer_avro.subscribe(['orders'])

consumer_retry = Consumer(consumer_conf_retry)
consumer_retry.subscribe(['orders-retry'])

# Retry Producer
retry_producer = Producer({'bootstrap.servers': 'localhost:9092'})

# DLQ Producer
dlq_producer = Producer({'bootstrap.servers': 'localhost:9092'})

# Aggregation variables
total_price = 0.0
order_count = 0
running_avg = 0.0

# Retry configuration
MAX_RETRIES = 3

def process_order(order, retry_count=0, from_retry_topic=False):
    
    try:
        # Simulate processing failure for prices < 20.0
        if order['price'] < 20.0 and retry_count < MAX_RETRIES:
            raise Exception('Temporary processing error')
        
        # Simulate permanent failure for very low prices
        if order['price'] < 15.0:
            raise Exception('Permanent processing error - price too low')
        
        # Successfully processed
        global total_price, order_count, running_avg
        total_price += order['price']
        order_count += 1
        running_avg = total_price / order_count
        
        topic_source = "RETRY" if from_retry_topic else "MAIN"
        print(f"✓ Processed [{topic_source}]: OrderID={order['orderId']}, Product={order['product']}, Price=${order['price']:.2f}")
        print(f"  Running Average: ${running_avg:.2f} (Total Orders: {order_count})\n")
        return True
        
    except Exception as e:
        if retry_count < MAX_RETRIES:
            print(f"⚠ Retry {retry_count + 1}/{MAX_RETRIES} for OrderID={order['orderId']}: {e}")
            
            # Send to retry topic with retry count
            retry_message = {
                'orderId': order['orderId'],
                'product': order['product'],
                'price': order['price'],
                'retry_count': retry_count + 1
            }
            
            retry_producer.produce(
                'orders-retry',
                key=order['orderId'],
                value=json.dumps(retry_message)
            )
            retry_producer.flush()
            print(f"  → Sent to orders-retry topic\n")
            return None
        else:
            # Send to DLQ
            print(f"✗ FAILED PERMANENTLY - Sending OrderID={order['orderId']} to DLQ")
            print(f"  Reason: {e}\n")
            dlq_producer.produce('orders-dlq', key=order['orderId'], value=str(order))
            dlq_producer.flush()
            return False

# Consume messages
try:
    print("=== Order Consumer Started ===")
    print("Subscribed to: orders (Avro), orders-retry (String)")
    print("Waiting for messages...\n")
    
    while True:
        # Poll from main orders topic (Avro)
        msg_avro = consumer_avro.poll(0.1)
        if msg_avro is not None and not msg_avro.error():
            order = msg_avro.value()
            process_order(order, retry_count=0, from_retry_topic=False)
        
        # Poll from retry topic (String)
        msg_retry = consumer_retry.poll(0.1)
        if msg_retry is not None and not msg_retry.error():
            retry_data = json.loads(msg_retry.value().decode('utf-8'))
            order = {
                'orderId': retry_data['orderId'],
                'product': retry_data['product'],
                'price': retry_data['price']
            }
            retry_count = retry_data.get('retry_count', 1)
            
            # Wait before retrying
            time.sleep(2)
            print(f" Processing from RETRY topic (Attempt {retry_count})...")
            process_order(order, retry_count=retry_count, from_retry_topic=True)
        
        time.sleep(0.1)
        
except KeyboardInterrupt:
    print('\n=== Consumer Stopped ===')
finally:
    consumer_avro.close()
    consumer_retry.close()