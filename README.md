# Kafka Producer-Consumer Project

A Python-based Apache Kafka producer and consumer application with Avro schema support for message serialization.

## Project Structure

```
Kafka_Producer/
├── producer/
│   └── producer.py          # Kafka producer implementation
├── consumer/
│   └── consumer.py          # Kafka consumer implementation
├── schema/
│   └── order.avsc           # Avro schema definition
├── docker-compose.yml       # Docker compose configuration for Kafka setup
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## Features

- **Kafka Producer**: Sends messages to Kafka topics with Avro serialization
- **Kafka Consumer**: Consumes and processes messages from Kafka topics
- **Avro Schema Support**: Uses Avro for efficient and schema-validated message serialization
- **Docker Support**: Easy setup with Docker Compose for local Kafka development

## Prerequisites

- Python 3.7+
- Docker and Docker Compose (for running Kafka locally)
- pip (Python package manager)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd Kafka_Producer
```

2. Create and activate virtual environment (optional but recommended):
```bash
python -m venv _bimbi_kafka
# On Windows:
_bimbi_kafka\Scripts\activate
# On Linux/Mac:
source _bimbi_kafka/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Setup

### Start Kafka with Docker Compose

```bash
docker-compose up -d
```

This will start:
- Zookeeper
- Kafka broker

To stop:
```bash
docker-compose down
```

## Usage

### Running the Producer

```bash
python producer/producer.py
```

The producer will send messages to a Kafka topic using the Avro schema defined in `schema/order.avsc`.

### Running the Consumer

```bash
python consumer/consumer.py
```

The consumer will read messages from the Kafka topic and deserialize them using the Avro schema.

## Configuration

### Kafka Connection

Update the Kafka broker address in producer and consumer files as needed:
- Default: `localhost:9092`

### Avro Schema

The schema for messages is defined in `schema/order.avsc`. Modify this file to change the message structure.

## Dependencies

Key dependencies (see `requirements.txt`):
- `confluent-kafka`: Kafka client for Python
- `fastavro`: Fast Avro serialization/deserialization
- `requests`: HTTP library

## Testing

To test the producer and consumer:

1. Start Kafka:
```bash
docker-compose up -d
```

2. Run the consumer in one terminal:
```bash
python consumer/consumer.py
```

3. Run the producer in another terminal:
```bash
python producer/producer.py
```

4. Verify messages are being consumed correctly

## Troubleshooting

### Connection Issues
- Ensure Kafka is running: `docker-compose ps`
- Check Kafka logs: `docker-compose logs kafka`

### Schema Issues
- Verify the Avro schema in `schema/order.avsc` is valid JSON
- Ensure both producer and consumer use the same schema

### Dependency Issues
- Reinstall requirements: `pip install -r requirements.txt --force-reinstall`

## License

[Add your license information here]

## Contributing

[Add contribution guidelines here]
