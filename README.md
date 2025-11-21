# Bimbi Kafka Producer-Consumer

A Python-based Kafka application demonstrating event streaming with Apache Kafka, featuring a producer that generates orders and a consumer that processes them with retry logic and dead-letter queue (DLQ) handling.

## Overview

This project showcases a complete Kafka workflow with:
- **Order Producer**: Generates order messages with Avro serialization
- **Order Consumer**: Processes orders with failure handling, retries, and aggregation
- **Schema Registry**: Manages Avro schemas for data validation
- **Kafka UI**: Web interface for monitoring Kafka clusters

## Architecture

```
Producer (Avro) → orders topic → Consumer → Processing Logic
                                    ├→ orders-retry topic (transient failures)
                                    └→ orders-dlq topic (permanent failures)
```

## Prerequisites

- Python 3.8+
- Docker & Docker Compose
- pip (Python package manager)

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/Pasindu2000B/Kafka_Producer_Consumer.git
cd Bimbi-Kafka
```

### 2. Set Up Virtual Environment
```bash
python -m venv _bimbi_kafka
source _bimbi_kafka/Scripts/activate  # Windows
# or
source _bimbi_kafka/bin/activate      # Linux/Mac
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

## Quick Start

### Start Kafka Infrastructure

Launch all required services (Zookeeper, Kafka, Schema Registry, Kafka UI):

```bash
docker-compose up -d
```

**Services**:
- **Kafka**: `localhost:9092`
- **Schema Registry**: `localhost:8082`
- **Kafka UI**: `http://localhost:8080`
- **Zookeeper**: `localhost:2181`

### Run Producer

In a terminal window:

```bash
python producer/producer.py
```

The producer will generate orders every 2 seconds with:
- Random products (Item1-Item5)
- 80% normal prices ($30-$100)
- 20% low prices ($10-$25) to trigger retries

### Run Consumer

In another terminal window:

```bash
python consumer/consumer.py
```

The consumer will:
- Process orders from the main `orders` topic
- Automatically retry failed orders (price < $20)
- Send permanent failures to the DLQ
- Display running statistics and metrics

## Project Structure

```
Bimbi-Kafka/
├── producer/
│   └── producer.py              # Order producer with Avro serialization
├── consumer/
│   └── consumer.py              # Order consumer with retry & DLQ logic
├── schema/
│   └── order.avsc               # Avro schema definition
├── docker-compose.yml           # Infrastructure as Code
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## Configuration

### Producer Configuration
- **Bootstrap Servers**: `localhost:9092`
- **Topic**: `orders`
- **Serializer**: Avro
- **Message Interval**: 2 seconds

### Consumer Configuration
- **Bootstrap Servers**: `localhost:9092`
- **Consumer Group**: `order-consumer-group`
- **Topics**: `orders`, `orders-retry`
- **Auto Commit**: Enabled (1000ms interval)
- **Max Retries**: 3 attempts

### Order Schema (Avro)

```json
{
  "type": "record",
  "name": "Order",
  "namespace": "com.bimbi.kafka",
  "fields": [
    {"name": "orderId", "type": "string"},
    {"name": "product", "type": "string"},
    {"name": "price", "type": "float"}
  ]
}
```

## Processing Rules

### Success Criteria
- Price ≥ $20.00

### Retry Criteria
- Price: $15.00 - $19.99
- Retries: Up to 3 attempts
- Topic: `orders-retry`
- Delay: 2 seconds between retries

### Dead-Letter Queue (DLQ)
- Price: < $15.00 (permanent failures)
- Topic: `orders-dlq`
- Action: Message is discarded after reaching max retries

## Dependencies

- **confluent-kafka[avro]** (2.12.2+): Kafka client with Avro support
- **fastavro** (1.12.1+): Fast Avro serialization

See `requirements.txt` for the complete list.

## Monitoring

### Using Kafka UI

1. Open `http://localhost:8080` in your browser
2. View topics, consumer groups, and messages in real-time
3. Monitor partition distribution and lag

### Consumer Output Example

```
=== Order Consumer Started ===
Subscribed to: orders (Avro), orders-retry (String)
Waiting for messages...

✓ Processed [MAIN]: OrderID=1001, Product=Item3, Price=$45.50
  Running Average: $45.50 (Total Orders: 1)

⚠ Retry 1/3 for OrderID=1002: Temporary processing error
  → Sent to orders-retry topic

Processing from RETRY topic (Attempt 1)...
✓ Processed [RETRY]: OrderID=1002, Product=Item1, Price=$18.75
  Running Average: $32.13 (Total Orders: 2)

✗ FAILED PERMANENTLY - Sending OrderID=1003 to DLQ
  Reason: Permanent processing error - price too low
```

## Troubleshooting

### Connection Issues
```
Error: Failed to connect to bootstrap server
→ Ensure Docker containers are running: docker-compose ps
```

### Schema Registry Errors
```
Error: Could not find schema
→ Verify schema-registry is accessible at http://localhost:8082
```

### Out of Memory
```
→ Increase Docker memory allocation: docker-compose down && docker-compose up -d
```

## Development

### Run Tests
```bash
pytest tests/
```

### Check Logs
```bash
# Producer logs
docker-compose logs kafka -f

# Consumer logs
docker logs <consumer-container-id>
```

### Stop Everything
```bash
docker-compose down
```

## Key Features

✅ **Avro Serialization**: Schema-driven data serialization with Schema Registry  
✅ **Retry Logic**: Automatic retry with configurable max attempts  
✅ **Dead-Letter Queue**: Failed messages preserved for analysis  
✅ **Running Aggregation**: Real-time statistics calculation  
✅ **Consumer Groups**: Horizontal scalability support  
✅ **Kafka UI**: Visual monitoring and management  

## Technologies Used

- **Apache Kafka 7.5.0**: Event streaming platform
- **Confluent Schema Registry 7.5.0**: Schema management
- **Python 3.8+**: Application runtime
- **Docker & Docker Compose**: Infrastructure orchestration
- **Avro**: Data serialization format

## Performance Notes

- Default message interval: 2 seconds
- Consumer polling: Non-blocking (0.1s timeout)
- Max retries: 3 attempts with 2-second delay
- Single-partition topics for simplicity

## License

MIT License - See LICENSE file for details

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/improvement`)
3. Commit changes (`git commit -am 'Add improvement'`)
4. Push to branch (`git push origin feature/improvement`)
5. Open a Pull Request

## Support

For issues and questions:
- Open an issue on GitHub
- Check existing documentation
- Review producer/consumer logs

## Author

**Pasindu2000B**  
Repository: [Kafka_Producer_Consumer](https://github.com/Pasindu2000B/Kafka_Producer_Consumer)

---

**Last Updated**: November 2025
