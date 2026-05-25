import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.core.kafka_producer import KafkaProducer
from app.core.redis_client import RedisClient
from app.core.kafka_consumer import KafkaConsumer


class TestKafkaProducer:
    """Test KafkaProducer functionality"""

    def test_producer_initialization(self):
        """Test producer is initialized with correct bootstrap servers"""
        producer = KafkaProducer(bootstrap_servers=["localhost:9092", "localhost:9093"])
        assert producer.bootstrap_servers == ["localhost:9092", "localhost:9093"]
        assert producer.producer is None

    @pytest.mark.asyncio
    async def test_producer_start(self):
        """Test producer can be started"""
        producer = KafkaProducer(bootstrap_servers=["localhost:9092"])
        with patch("app.core.kafka_producer.AIOKafkaProducer") as mock_producer_class:
            mock_producer_instance = AsyncMock()
            mock_producer_class.return_value = mock_producer_instance

            await producer.start()
            assert producer.producer is not None
            mock_producer_instance.start.assert_called_once()

    @pytest.mark.asyncio
    async def test_producer_stop(self):
        """Test producer can be stopped"""
        producer = KafkaProducer(bootstrap_servers=["localhost:9092"])
        with patch("app.core.kafka_producer.AIOKafkaProducer") as mock_producer_class:
            mock_producer_instance = AsyncMock()
            mock_producer_class.return_value = mock_producer_instance

            await producer.start()
            await producer.stop()
            mock_producer_instance.stop.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_success(self):
        """Test successful send returns True"""
        producer = KafkaProducer(bootstrap_servers=["localhost:9092"])
        with patch("app.core.kafka_producer.AIOKafkaProducer") as mock_producer_class:
            mock_producer_instance = AsyncMock()
            mock_producer_class.return_value = mock_producer_instance

            await producer.start()
            result = await producer.send("test-topic", {"event": "test"})

            assert result is True
            mock_producer_instance.send_and_wait.assert_called_once_with("test-topic", {"event": "test"})

    @pytest.mark.asyncio
    async def test_send_without_start_returns_false(self):
        """Test send returns False when producer not started"""
        producer = KafkaProducer(bootstrap_servers=["localhost:9092"])
        result = await producer.send("test-topic", {"event": "test"})
        assert result is False

    @pytest.mark.asyncio
    async def test_send_error_returns_false(self):
        """Test send returns False on error"""
        producer = KafkaProducer(bootstrap_servers=["localhost:9092"])
        with patch("app.core.kafka_producer.AIOKafkaProducer") as mock_producer_class:
            mock_producer_instance = AsyncMock()
            mock_producer_instance.send_and_wait.side_effect = Exception("Kafka error")
            mock_producer_class.return_value = mock_producer_instance

            await producer.start()
            result = await producer.send("test-topic", {"event": "test"})

            assert result is False


class TestRedisClient:
    """Test RedisClient functionality"""

    def test_redis_client_initialization(self):
        """Test RedisClient is initialized with correct URL"""
        client = RedisClient(url="redis://localhost:6379")
        assert client.url == "redis://localhost:6379"
        assert client.client is None

    @pytest.mark.asyncio
    async def test_connect(self):
        """Test client can connect"""
        client = RedisClient(url="redis://localhost:6379")
        with patch("app.core.redis_client.redis.from_url") as mock_from_url:
            mock_redis_instance = AsyncMock()
            mock_from_url.return_value = mock_redis_instance

            await client.connect()
            assert client.client is not None
            mock_from_url.assert_called_once()

    @pytest.mark.asyncio
    async def test_disconnect(self):
        """Test client can disconnect"""
        client = RedisClient(url="redis://localhost:6379")
        with patch("app.core.redis_client.redis.from_url") as mock_from_url:
            mock_redis_instance = AsyncMock()
            mock_from_url.return_value = mock_redis_instance

            await client.connect()
            await client.disconnect()
            mock_redis_instance.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_success(self):
        """Test successful get returns value"""
        client = RedisClient(url="redis://localhost:6379")
        with patch("app.core.redis_client.redis.from_url") as mock_from_url:
            mock_redis_instance = AsyncMock()
            mock_redis_instance.get.return_value = "test_value"
            mock_from_url.return_value = mock_redis_instance

            await client.connect()
            result = await client.get("test_key")

            assert result == "test_value"
            mock_redis_instance.get.assert_called_once_with("test_key")

    @pytest.mark.asyncio
    async def test_get_without_connect_raises_error(self):
        """Test get raises error when client not connected"""
        client = RedisClient(url="redis://localhost:6379")
        with pytest.raises(RuntimeError, match="Client not connected"):
            await client.get("test_key")

    @pytest.mark.asyncio
    async def test_set_success(self):
        """Test successful set"""
        client = RedisClient(url="redis://localhost:6379")
        with patch("app.core.redis_client.redis.from_url") as mock_from_url:
            mock_redis_instance = AsyncMock()
            mock_from_url.return_value = mock_redis_instance

            await client.connect()
            await client.set("test_key", "test_value")

            mock_redis_instance.set.assert_called_once_with("test_key", "test_value", ex=None)

    @pytest.mark.asyncio
    async def test_set_with_expire(self):
        """Test set with expire"""
        client = RedisClient(url="redis://localhost:6379")
        with patch("app.core.redis_client.redis.from_url") as mock_from_url:
            mock_redis_instance = AsyncMock()
            mock_from_url.return_value = mock_redis_instance

            await client.connect()
            await client.set("test_key", "test_value", ex=3600)

            mock_redis_instance.set.assert_called_once_with("test_key", "test_value", ex=3600)

    @pytest.mark.asyncio
    async def test_set_without_connect_raises_error(self):
        """Test set raises error when client not connected"""
        client = RedisClient(url="redis://localhost:6379")
        with pytest.raises(RuntimeError, match="Client not connected"):
            await client.set("test_key", "test_value")

    @pytest.mark.asyncio
    async def test_incr_success(self):
        """Test successful incr returns new value"""
        client = RedisClient(url="redis://localhost:6379")
        with patch("app.core.redis_client.redis.from_url") as mock_from_url:
            mock_redis_instance = AsyncMock()
            mock_redis_instance.incr.return_value = 5
            mock_from_url.return_value = mock_redis_instance

            await client.connect()
            result = await client.incr("counter_key")

            assert result == 5
            mock_redis_instance.incr.assert_called_once_with("counter_key")


class TestKafkaConsumer:
    """Test KafkaConsumer functionality"""

    def test_consumer_initialization(self):
        """Test consumer is initialized with correct parameters"""
        consumer = KafkaConsumer(
            bootstrap_servers=["localhost:9092"],
            group_id="test-group"
        )
        assert consumer.bootstrap_servers == ["localhost:9092"]
        assert consumer.group_id == "test-group"
        assert consumer.consumer is None

    @pytest.mark.asyncio
    async def test_consumer_start(self):
        """Test consumer can be started"""
        consumer = KafkaConsumer(
            bootstrap_servers=["localhost:9092"],
            group_id="test-group"
        )
        with patch("app.core.kafka_consumer.AIOKafkaConsumer") as mock_consumer_class:
            mock_consumer_instance = AsyncMock()
            mock_consumer_class.return_value = mock_consumer_instance

            await consumer.start()
            assert consumer.consumer is not None
            mock_consumer_class.assert_called_once()

    @pytest.mark.asyncio
    async def test_consumer_stop(self):
        """Test consumer can be stopped"""
        consumer = KafkaConsumer(
            bootstrap_servers=["localhost:9092"],
            group_id="test-group"
        )
        with patch("app.core.kafka_consumer.AIOKafkaConsumer") as mock_consumer_class:
            mock_consumer_instance = AsyncMock()
            mock_consumer_class.return_value = mock_consumer_instance

            await consumer.start()
            await consumer.stop()
            mock_consumer_instance.stop.assert_called_once()

    @pytest.mark.asyncio
    async def test_subscribe(self):
        """Test consumer can subscribe to topics"""
        consumer = KafkaConsumer(
            bootstrap_servers=["localhost:9092"],
            group_id="test-group"
        )
        with patch("app.core.kafka_consumer.AIOKafkaConsumer") as mock_consumer_class:
            mock_consumer_instance = AsyncMock()
            mock_consumer_class.return_value = mock_consumer_instance

            await consumer.start()
            await consumer.subscribe(["topic1", "topic2"])

            mock_consumer_instance.start.assert_called()
            mock_consumer_instance.subscribe.assert_called_once_with(["topic1", "topic2"])

    @pytest.mark.asyncio
    async def test_subscribe_without_start_raises_error(self):
        """Test subscribe raises error when consumer not started"""
        consumer = KafkaConsumer(
            bootstrap_servers=["localhost:9092"],
            group_id="test-group"
        )
        with pytest.raises(RuntimeError, match="Consumer not started"):
            await consumer.subscribe(["topic1"])