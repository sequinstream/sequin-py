# `sequin-py`

A lightweight Python SDK for sending, receiving, and acknowledging messages in [Sequin streams](https://github.com/sequinstream/sequin). For easy development and testing, it also comes with helpful methods for managing the lifecycle of streams and consumers.

## Installing

Install the library:

```shell
pip install sequin-py
```

## Initializing

You'll typically initialize a Sequin `Client` once in your application. Create a new file to initialize the `Client` in, and import it for use in other parts of your app:

```python
# sequin.py

from sequin_py import Client

base_url = os.environ.get('SEQUIN_URL', 'http://localhost:7376')

sequin = Client(base_url)
```

By default, the Client is initialized using Sequin's default host and port in local development: `http://localhost:7376`

## Usage

You'll predominantly use `sequin-py` to send, receive, and acknowledge [messages](https://github.com/sequinstream/sequin?tab=readme-ov-file#messages) in Sequin streams:

```python
# Import the Sequin client from sequin.py
from sequin import sequin

# Define your stream and consumer
stream = 'your-stream-name'
consumer = 'your-consumer-name'

# Send a message
res, error = sequin.send_message(stream, 'test.1', 'Hello, Sequin!')
if error:
    print(f"Error sending message: {error['summary']}")
    # Handle the error appropriately
else:
    print(f"Message sent successfully: {res}")

# Receive a message
message, error = sequin.receive_message(stream, consumer)
if error:
    print(f"Error receiving message: {error['summary']}")
elif message is None:
    print("No messages available")
else:
    print(f"Received message: {message}")
    # Don't forget to acknowledge the message
    ack_res, ack_error = sequin.ack_message(stream, consumer, message['ack_id'])
    if ack_error:
        print(f"Error acking message: {ack_error['summary']}")
    else:
        print("Message acked")
```

### `send_message()`

[Send](https://github.com/sequinstream/sequin?tab=readme-ov-file#sending-messages) a message to a stream:

```python
res, error = sequin.send_message(stream_id_or_name: str, key: str, data: str)
```

#### Parameters

`send_message()` accepts three arguments:

- `stream_id_or_name` (_str_): Either the name or id of the stream.
- `key` (_str_): The key for the message.
- `data` (_str_): The data payload for the message as a string.

#### Returns

`send_message()` will return a tuple `(res, error)`:

**Success**

```python
res = {
    "published": 1
}
error = None
```

**Error**

```python
res = None
error = {
    "status": 404,
    "summary": "stream not found"
}
```

#### Example

```python
res, error = sequin.send_message('my_stream', 'greeting.1', 'Hello, Sequin!')
if error:
    print(f"Error sending message: {error['summary']}")
    # Handle the error appropriately
else:
    print(f"Message sent successfully: {res['published']}")
```

### `send_messages()`

Send a batch of messages (max 1,000):

```python
res, error = sequin.send_messages(stream_id_or_name: str, messages: list)
```

#### Parameters

`send_messages()` accepts two arguments:

- `stream_id_or_name` (_str_): Either the name or id of the stream.
- `messages` (_list_): A list of message dictionaries:

```python
[
    {
        "key": "message_key_1",
        "data": "data_payload_1"
    },
    {
        "key": "message_key_2",
        "data": "data_payload_2"
    },
    # ...
]
```

#### Returns

`send_messages()` will return a tuple `(res, error)`:

> [!IMPORTANT]
> `send_messages()` is all or nothing. Either all the messages are successfully published, or none of the messages are published.

**Success**

```python
res = {
    "published": 42
}
error = None
```

**Error**

```python
res = None
error = {
    "status": 404,
    "summary": "Stream not found"
}
```

#### Example

```python
messages = [
    {
        "key": "test.1",
        "data": "Hello, Sequin!"
    },
    {
        "key": "test.2",
        "data": "Greetings from Sequin!"
    }
]

res, error = sequin.send_messages('my_stream', messages)
if error:
    print(f"Error sending messages: {error['summary']}")
    # Handle the error appropriately
else:
    print(f"Messages sent successfully: {res['published']}")
```

### `receive_message()`

To pull a single message off the stream using a Sequin consumer, you'll use the `receive_message()` function:

```python
message, error = sequin.receive_message(stream_id_or_name: str, consumer_id_or_name: str)
```

#### Parameters

`receive_message()` accepts two arguments:

- `stream_id_or_name` (_str_): Either the name or id of the stream.
- `consumer_id_or_name` (_str_): Either the name or id of the consumer.

#### Returns

`receive_message()` will return a tuple `(message, error)`:

**No messages available**

```python
message = None
error = None
```

**Message**

```python
message = {
    "message": {
        "key": "test.1",
        "stream_id": "def45b2d-ae3f-46a4-b57b-54cdc1cecc6d",
        "data": "Hello, Sequin!",
        "seq": 1,
        "inserted_at": "2024-07-23T00:31:55.668060Z",
        "updated_at": "2024-07-23T00:31:55.668060Z"
    },
    "ack_id": "07240856-96cb-4305-9b2f-620f4b1528a4"
}
error = None
```

**Error**

```python
message = None
error = {
    "status": 404,
    "summary": "Consumer not found."
}
```

#### Example

```python
message, error = sequin.receive_message('my_stream', 'my_consumer')
if error:
    print(f"Error receiving message: {error['summary']}")
    # Handle the error appropriately
elif message is None:
    print("No messages available")
else:
    print(f"Message received successfully: {message}")
```

### `receive_messages()`

You can pull a batch of messages for your consumer using `receive_messages()`. `receive_messages()` pulls a batch of `10` messages by default:

```python
messages, error = sequin.receive_messages(stream_id_or_name: str, consumer_id_or_name: str, options: Optional[dict] = None)
```

#### Parameters

`receive_messages()` accepts three arguments:

- `stream_id_or_name` (_str_): Either the name or id of the stream.
- `consumer_id_or_name` (_str_): Either the name or id of the consumer.
- `options` (_dict_, optional): A dictionary that defines optional parameters:
  - `batch_size` (int): The number of messages to request. Default is 10, max of 1,000.

```python
options = {
    "batch_size": int  # The number of messages to request. Default is 10, max of 1,000.
}
```

#### Returns

`receive_messages()` will return a tuple `(messages, error)`:

**No messages available**

```python
messages = []
error = None
```

**Messages**

```python
messages = [
    {
        "message": {
            "key": "test.1",
            "stream_id": "def45b2d-ae3f-46a4-b57b-54cdc1cecc6d",
            "data": "Hello, Sequin!",
            "seq": 1,
            "inserted_at": "2024-07-23T00:31:55.668060Z",
            "updated_at": "2024-07-23T00:31:55.668060Z"
        },
        "ack_id": "07240856-96cb-4305-9b2f-620f4b1528a4"
    },
    # ... more messages
]
error = None
```

**Error**

```python
messages = None
error = {
    "status": 404,
    "summary": "Consumer not found."
}
```

#### Example

```python
messages, error = sequin.receive_messages('my_stream', 'my_consumer', options={'batch_size': 100})
if error:
    print(f"Error receiving messages: {error['summary']}")
    # Handle the error appropriately
elif not messages:
    print("No messages available")
else:
    print(f"Messages received successfully: {len(messages)}")
```

### `ack_message()`

To acknowledge a message, use the `ack_message()` function:

```python
res, error = sequin.ack_message(stream_id_or_name: str, consumer_id_or_name: str, ack_id: str)
```

#### Parameters

`ack_message()` accepts three arguments:

- `stream_id_or_name` (_str_): Either the name or id of the stream.
- `consumer_id_or_name` (_str_): Either the name or id of the consumer.
- `ack_id` (_str_): The acknowledgement ID of the message.

#### Returns

`ack_message()` will return a tuple `(res, error)`:

**Success**

```python
res = {
    "success": True
}
error = None
```

**Error**

```python
res = None
error = {
    "status": 404,
    "summary": "Consumer not found."
}
```

#### Example

```python
res, error = sequin.ack_message('my_stream', 'my_consumer', '07240856-96cb-4305-9b2f-620f4b1528a4')
if error:
    print(f"Error acknowledging message: {error['summary']}")
    # Handle the error appropriately
else:
    print("Message acknowledged successfully")
```

### `ack_messages()`

To acknowledge multiple messages at once, use the `ack_messages()` function:

```python
res, error = sequin.ack_messages(stream_id_or_name: str, consumer_id_or_name: str, ack_ids: List[str])
```

#### Parameters

`ack_messages()` accepts three arguments:

- `stream_id_or_name` (_str_): Either the name or id of the stream.
- `consumer_id_or_name` (_str_): Either the name or id of the consumer.
- `ack_ids` (_List[str]_): A list of acknowledgement IDs of the messages to acknowledge.

#### Returns

`ack_messages()` will return a tuple `(res, error)`:

**Success**

```python
res = {
    "success": True
}
error = None
```

**Error**

```python
res = None
error = {
    "status": 404,
    "summary": "Consumer not found."
}
```

#### Example

```python
ack_ids = ['07240856-96cb-4305-9b2f-620f4b1528a4', '18351967-07dc-5416-0c2e-731f5b2638b5']
res, error = sequin.ack_messages('my_stream', 'my_consumer', ack_ids)
if error:
    print(f"Error acknowledging messages: {error['summary']}")
    # Handle the error appropriately
else:
    print("Messages acknowledged successfully")
```

### `nack_message()`

To negatively acknowledge a message (indicating it couldn't be processed), use the `nack_message()` function:

```python
res, error = sequin.nack_message(stream_id_or_name: str, consumer_id_or_name: str, ack_id: str)
```

#### Parameters

`nack_message()` accepts three arguments:

- `stream_id_or_name` (_str_): Either the name or id of the stream.
- `consumer_id_or_name` (_str_): Either the name or id of the consumer.
- `ack_id` (_str_): The acknowledgement ID of the message to negatively acknowledge.

#### Returns

`nack_message()` will return a tuple `(res, error)`:

**Success**

```python
res = {
    "success": True
}
error = None
```

**Error**

```python
res = None
error = {
    "status": 404,
    "summary": "Consumer not found."
}
```

#### Example

```python
res, error = sequin.nack_message('my_stream', 'my_consumer', '07240856-96cb-4305-9b2f-620f4b1528a4')
if error:
    print(f"Error nacking message: {error['summary']}")
    # Handle the error appropriately
else:
    print("Message nacked successfully")
```

### `nack_messages()`

To negatively acknowledge multiple messages at once, use the `nack_messages()` function:

```python
res, error = sequin.nack_messages(stream_id_or_name: str, consumer_id_or_name: str, ack_ids: List[str])
```

#### Parameters

`nack_messages()` accepts three arguments:

- `stream_id_or_name` (_str_): Either the name or id of the stream.
- `consumer_id_or_name` (_str_): Either the name or id of the consumer.
- `ack_ids` (_List[str]_): A list of acknowledgement IDs of the messages to negatively acknowledge.

#### Returns

`nack_messages()` will return a tuple `(res, error)`:

**Success**

```python
res = {
    "success": True
}
error = None
```

**Error**

```python
res = None
error = {
    "status": 404,
    "summary": "Consumer not found."
}
```

#### Example

```python
ack_ids = ['07240856-96cb-4305-9b2f-620f4b1528a4', '18351967-07dc-5416-0c2e-731f5b2638b5']
res, error = sequin.nack_messages('my_stream', 'my_consumer', ack_ids)
if error:
    print(f"Error nacking messages: {error['summary']}")
    # Handle the error appropriately
else:
    print("Messages nacked successfully")
```

### `create_stream()`

Creating streams can be helpful in automated testing. You can create a new stream using `create_stream()`:

```python
stream, error = sequin.create_stream(stream_name: str, options: Optional[dict] = None)
```

#### Parameters

`create_stream()` accepts two parameters:

- `stream_name` (_str_): The name of the stream you want to create.
- `options` (_dict_, optional): A dictionary of key-value pairs that define optional parameters:
  - `one_message_per_key` (_bool_)
  - `process_unmodified` (_bool_)
  - `max_storage_gb` (_int_)
  - `retain_up_to` (_int_)
  - `retain_at_least` (_int_)

```python
options = {
    "one_message_per_key": True,
    "process_unmodified": False,
    "max_storage_gb": 10,
    "retain_up_to": 1000000,
    "retain_at_least": 100000
}
```

#### Returns

`create_stream()` will return a tuple `(stream, error)`:

**Success**

```python
stream = {
    "id": "197a3ee8-8ddd-4ddd-8456-5d0b78a72784",
    "name": "my_stream",
    "account_id": "8b930c30-2334-4339-b7ba-f250b7be223e",
    "stats": {
        "message_count": 0,
        "consumer_count": 0,
        "storage_size": 163840
    },
    "inserted_at": "2024-07-24T20:02:46Z",
    "updated_at": "2024-07-24T20:02:46Z"
}
error = None
```

**Error**

```python
stream = None
error = {
    "status": 422,
    "summary": "Validation failed: duplicate name"
}
```

#### Example

```python
stream, error = sequin.create_stream('my_stream')
if error:
    print(f"Error creating stream: {error['summary']}")
    # Handle the error appropriately
else:
    print(f"Stream created successfully: {stream}")
```

### `delete_stream()`

Deleting streams can be helpful in automated testing. You can delete a stream using `delete_stream()`:

```python
res, error = sequin.delete_stream(stream_id_or_name: str)
```

#### Parameters

`delete_stream()` accepts one parameter:

- `stream_id_or_name` (_str_): The id or name of the stream you want to delete.

#### Returns

`delete_stream()` will return a tuple `(res, error)`:

**Successful delete**

```python
res = {
    "id": "197a3ee8-8ddd-4ddd-8456-5d0b78a72784",
    "deleted": True
}
error = None
```

**Error**

```python
res = None
error = {
    "status": 404,
    "summary": "Not found: No `stream` found matching the provided ID or name"
}
```

#### Example

```python
res, error = sequin.delete_stream('my_stream')
if error:
    print(f"Error deleting stream: {error['summary']}")
    # Handle the error appropriately
else:
    print(f"Stream deleted successfully: {res}")
```

### `create_consumer()`

Creating [consumers](https://github.com/sequinstream/sequin?tab=readme-ov-file#consumers-1) can be helpful in automated testing. You can create a new consumer using `create_consumer()`:

```python
consumer, error = sequin.create_consumer(stream_id_or_name: str, consumer_name: str, consumer_filter: str, options: Optional[dict] = None)
```

#### Parameters

`create_consumer()` accepts four parameters:

- `stream_id_or_name` (_str_): The id or name of the stream you want to attach the consumer to.
- `consumer_name` (_str_): The name of the consumer you want to create.
- `consumer_filter` (_str_): The filter pattern the consumer will use to pull messages off the stream.
- `options` (_dict_, optional): A dictionary of key-value pairs that define optional parameters:
  - `ack_wait_ms` (_int_): Acknowledgement wait time in milliseconds
  - `max_ack_pending` (_int_): Maximum number of pending acknowledgements
  - `max_deliver` (_int_): Maximum number of delivery attempts

```python
options = {
    "ack_wait_ms": 60000,
    "max_ack_pending": 5000,
    "max_deliver": 3
}
```

#### Returns

`create_consumer()` will return a tuple `(consumer, error)`:

**Success**

```python
consumer = {
    "ack_wait_ms": 30000,
    "filter_key_pattern": "test.>",
    "id": "67df6362-ba21-4ddc-8601-55d404bacaeb",
    "inserted_at": "2024-07-24T20:12:20Z",
    "kind": "pull",
    "max_ack_pending": 10000,
    "max_deliver": None,
    "max_waiting": 20,
    "name": "my_consumer",
    "stream_id": "15b1f003-3a47-4371-8331-6437cb48477e",
    "updated_at": "2024-07-24T20:12:20Z",
    "status": "active"
}
error = None
```

**Error**

```python
consumer = None
error = {
    "status": 422,
    "summary": "Validation failed: duplicate name"
}
```

#### Example

```python
consumer, error = sequin.create_consumer('my_stream', 'my_consumer', 'test.>')
if error:
    print(f"Error creating consumer: {error creating consumer: {error['summary']}")
    # Handle the error appropriately
else:
    print(f"Consumer created successfully: {consumer}")
```

### `delete_consumer()`

Deleting consumers can be helpful in automated testing. You can delete a consumer using `delete_consumer()`:

```python
res, error = sequin.delete_consumer(stream_id_or_name: str, consumer_id_or_name: str)
```

#### Parameters

`delete_consumer()` accepts two parameters:

- `stream_id_or_name` (_str_): The id or name of the stream associated to the consumer you want to delete.
- `consumer_id_or_name` (_str_): The id or name of the consumer you want to delete.

#### Returns

`delete_consumer()` will return a tuple `(res, error)`:

**Successful delete**

```python
res = {
    "id": "197a3ee8-8ddd-4ddd-8456-5d0b78a72784",
    "deleted": True
}
error = None
```

**Error**

```python
res = None
error = {
    "status": 404,
    "summary": "Not found: No `consumer` found matching the provided ID or name"
}
```

#### Example

```python
res, error = sequin.delete_consumer('my_stream', 'my_consumer')
if error:
    print(f"Error deleting consumer: {error['summary']}")
    # Handle the error appropriately
else:
    print(f"Consumer deleted successfully: {res}")
```

## Testing

To adequately test Sequin, we recommend creating temporary streams and consumers in addition to testing sending and receiving messages. Here's an example using pytest:

```python
import pytest
from sequin import sequin
import time

def test_sequin_stream_and_consumer():
    stream_name = f"test-stream-{int(time.time())}"
    consumer_name = f"test-consumer-{int(time.time())}"

    # Create a new stream
    stream, error = sequin.create_stream(stream_name)
    assert error is None
    assert stream['name'] == stream_name

    # Create a consumer
    consumer, error = sequin.create_consumer(stream_name, consumer_name, 'test.>')
    assert error is None
    assert consumer['name'] == consumer_name

    # Send a message
    res, error = sequin.send_message(stream_name, 'test.1', 'Hello, Sequin!')
    assert error is None
    assert res['published'] == 1

    # Receive and ack a message
    message, error = sequin.receive_message(stream_name, consumer_name)
    assert error is None
    assert message is not None

    res, error = sequin.ack_message(stream_name, consumer_name, message['ack_id'])
    assert error is None

    # Delete the consumer
    res, error = sequin.delete_consumer(stream_name, consumer_name)
    assert error is None
    assert res['deleted'] is True

    # Delete the stream
    res, error = sequin.delete_stream(stream_name)
    assert error is None
    assert res['deleted'] is True
```

This test creates a temporary stream and consumer, sends a message, receives and acknowledges it, and then cleans up by deleting the consumer and stream. You can expand on this basic test to cover more of your specific use cases and edge cases.
