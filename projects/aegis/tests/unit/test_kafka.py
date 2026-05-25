import pytest
from app.core.kafka_producer import KafkaProducer

@pytest.fixture
def producer():
    return KafkaProducer(bootstrap_servers=["localhost:9092"])

def test_producer_initialization(producer):
    assert producer.bootstrap_servers == ["localhost:9092"]
    assert producer.producer is None
