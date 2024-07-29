import pytest
from sequin.client import Client
import time

@pytest.fixture(scope="session")
def client():
    return Client(base_url='http://localhost:7376')

@pytest.fixture(scope="session")
def test_stream_name():
    return f'test_stream'

@pytest.fixture(scope="session")
def test_consumer_name():
    return f'test_consumer'

@pytest.fixture(scope="session", autouse=True)
def cleanup(client, test_stream_name, request):
    # Teardown: delete the stream
    def fin():
        client.delete_stream(test_stream_name)
    request.addfinalizer(fin)

def test_init_creates_client_instance(client):
    assert isinstance(client, Client)

def test_create_stream(client, test_stream_name):
    res, error = client.create_stream(test_stream_name)
    assert error is None
    assert res['name'] == test_stream_name

@pytest.mark.skip(reason="Not implemented yet")
def test_create_stream_with_all_properties(client):
    stream_name = f'test_stream_full_{int(time.time())}'
    res, error = client.create_stream(stream_name, {
        'max_storage_gb': 2,
        'one_message_per_key': True,
        'process_unmodified': False,
        'retain_up_to': 1000,
        'retain_at_least': 100
    })
    assert error is None
    assert res['name'] == stream_name
    assert 'account_id' in res
    assert 'stats' in res
    assert 'inserted_at' in res
    assert 'updated_at' in res
    # Clean up
    client.delete_stream(stream_name)

def test_send_message(client, test_stream_name):
    res, error = client.send_message(test_stream_name, 'test.1', 'value1')
    assert error is None
    assert res['published'] == 1

def test_send_messages(client, test_stream_name):
    messages = [
        {'key': 'test.2', 'data': 'value2'},
        {'key': 'test.3', 'data': 'value3'}
    ]
    res, error = client.send_messages(test_stream_name, messages)
    assert error is None
    assert res['published'] == 2

def test_create_consumer(client, test_stream_name, test_consumer_name):
    res, error = client.create_consumer(test_stream_name, test_consumer_name, 'test.>')
    assert error is None
    assert res['name'] == test_consumer_name

def test_create_consumer_with_options(client, test_stream_name):
    consumer_name = f'test_consumer_full_{int(time.time())}'
    res, error = client.create_consumer(test_stream_name, consumer_name, 'test.>', {
        'ack_wait_ms': 60000,
        'max_ack_pending': 5000,
        'max_deliver': 3
    })
    assert error is None
    assert res['name'] == consumer_name
    assert res['ack_wait_ms'] == 60000
    assert res['max_ack_pending'] == 5000
    assert res['max_deliver'] == 3
    # Clean up
    client.delete_consumer(test_stream_name, consumer_name)

def test_receive_message(client, test_stream_name, test_consumer_name):
    res, error = client.receive_message(test_stream_name, test_consumer_name)
    assert error is None
    assert 'message' in res
    assert 'ack_id' in res

def test_receive_messages(client, test_stream_name, test_consumer_name):
    res, error = client.receive_messages(test_stream_name, test_consumer_name, {'batch_size': 2})
    assert error is None
    assert len(res) == 2

def test_receive_message_no_messages(client, test_stream_name, test_consumer_name):
    # Ensure the stream is empty first
    client.receive_messages(test_stream_name, test_consumer_name, {'batch_size': 1000})
    res, error = client.receive_message(test_stream_name, test_consumer_name)
    assert error is None
    assert res is None

def test_receive_messages_custom_batch_size(client, test_stream_name, test_consumer_name):
    # Send 10 messages first
    messages = [{'key': f'test.{i}', 'data': f'value_{i}'} for i in range(10)]
    client.send_messages(test_stream_name, messages)

    res, error = client.receive_messages(test_stream_name, test_consumer_name, {'batch_size': 3})
    assert error is None
    assert len(res) == 3

def test_ack_messages(client, test_stream_name, test_consumer_name):
    res, error = client.receive_messages(test_stream_name, test_consumer_name, {'batch_size': 2})
    ack_ids = [msg['ack_id'] for msg in res]
    res, error = client.ack_messages(test_stream_name, test_consumer_name, ack_ids)
    assert error is None
    assert res == {'success': True}

def test_nack_messages(client, test_stream_name, test_consumer_name):
    res, error = client.receive_messages(test_stream_name, test_consumer_name, {'batch_size': 2})
    ack_ids = [msg['ack_id'] for msg in res]
    res, error = client.nack_messages(test_stream_name, test_consumer_name, ack_ids)
    assert error is None
    assert res == {'success': True}

def test_ack_message(client, test_stream_name, test_consumer_name):
    # Send a message first
    client.send_message(test_stream_name, 'test.ack', 'ack_value')

    # Receive the message
    res, error = client.receive_message(test_stream_name, test_consumer_name)
    assert res is not None

    # Acknowledge the message
    res, error = client.ack_message(test_stream_name, test_consumer_name, res['ack_id'])
    assert error is None
    assert res == {'success': True}

def test_nack_message(client, test_stream_name, test_consumer_name):
    # Send a message first
    client.send_message(test_stream_name, 'test.nack', 'nack_value')

    # Receive the message
    res, error = client.receive_message(test_stream_name, test_consumer_name)
    assert res is not None

    # Negative-acknowledge the message
    res, error = client.nack_message(test_stream_name, test_consumer_name, res['ack_id'])
    assert error is None
    assert res == {'success': True}

def test_delete_consumer(client, test_stream_name, test_consumer_name):
    res, error = client.delete_consumer(test_stream_name, test_consumer_name)
    assert error is None
    assert res['deleted'] is True

def test_delete_stream(client):
    temp_stream_name = f'temp_stream_{int(time.time())}'
    client.create_stream(temp_stream_name)
    res, error = client.delete_stream(temp_stream_name)
    assert error is None
    assert res['deleted'] is True

def test_handle_api_request_errors(client):
    res, error = client.send_message('non_existent_stream', 'testKey', 'testValue')
    assert res is None
    assert error is not None
    assert 'status' in error
    assert 'summary' in error

def test_misconfigured_client_returns_friendly_error():
    bad_client = Client(base_url='http://localhost:0000')
    res, error = bad_client.create_stream('test_stream')
    assert res is None
    assert error['status'] == 500
    assert "We can't reach Sequin" in error['summary']