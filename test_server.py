import pytest
from server import FileSearchServer
import socket
import threading
import ssl
import time

# Mock configurations for testing
class MockConfig:
    def __init__(self, path='./200k.txt', reread=True, ssl=True):
        self.linuxpath = path
        self.reread_on_query = reread
        self.ssl_enabled = ssl
        self.host = 'localhost'
        self.port = 12345

@pytest.fixture
def server(tmp_path):
    """Fixture to set up and tear down the server for testing."""
    # Create a temporary test file
    test_file = tmp_path / '200k.txt'
    test_file.write_text('teststring\n')

    config = MockConfig(path=str(test_file))
    server = FileSearchServer(host=config.host, port=config.port, linuxpath=config.linuxpath, reread_on_query=config.reread_on_query, ssl_enabled=config.ssl_enabled)
    server_thread = threading.Thread(target=server.start, daemon=True)
    server_thread.start()
    time.sleep(1)  # Give the server a moment to start
    yield server
    server.server_socket.close()

@pytest.fixture
def client():
    """Fixture to set up and tear down the client for testing."""
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    yield client_socket
    client_socket.close()

def ssl_wrap_socket(sock):
    context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    wrapped_socket = context.wrap_socket(sock, server_hostname='localhost')
    return wrapped_socket

def test_empty_query(server, client):
    try:
        client.sendall(b'')
        response = client.recv(1024).decode('utf-8')
        assert response == 'ERROR: Empty query\n'
    except (ConnectionError, BrokenPipeError) as e:
        pytest.fail(f"Connection error occurred: {e}")
    finally:
        client.close()  # Ensure client connection is closed

def test_non_existent_file():
    # Assuming FileSearchServer class or a similar server setup
    server = FileSearchServer('non_existent_file.txt', 'localhost', 12345, 'server.crt', 'server.key')
    server.start()
    client = socket.create_connection(('localhost', 12345))
    wrapped_client = ssl.wrap_socket(client, ca_certs='server.crt', cert_reqs=ssl.CERT_REQUIRED)
    wrapped_client.sendall(b'test query')
    response = wrapped_client.recv(1024).decode('utf-8')
    assert response == 'ERROR: File not found\n'
    wrapped_client.close()

def test_string_not_found(server, client):
    try: 
        client.sendall(b'nonexistentstring')
        response = client.recv(1024).decode('utf-8')
        assert response == 'STRING NOT FOUND\n'
    except (ConnectionError, BrokenPipeError) as e:
        pytest.fail(f"Connection error occurred: {e}")
    finally:
        client.close()  # Ensure client connection is closed

def test_string_exists(server, client):
    try:
        client.sendall(b'example')
        response = client.recv(1024).decode('utf-8')
        assert response == 'STRING EXISTS\n'
    except (ConnectionError, BrokenPipeError) as e:
        pytest.fail(f"Connection error occurred: {e}")
    finally:
        client.close()  # Ensure client connection is closed

if __name__ == '__main__':
    pytest.main()
