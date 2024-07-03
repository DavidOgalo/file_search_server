import pytest
from server import FileSearchServer
import socket
import threading
import ssl
import time
import os

# Mock configurations for testing
class MockConfig:
    def __init__(self, path='./200k.txt', reread=True, ssl=True):
        self.linuxpath = path
        self.reread_on_query = reread
        self.ssl_enabled = ssl
        self.host = 'localhost'
        self.port = 12345

@pytest.fixture
def server():
    config = MockConfig()
    server = FileSearchServer(host=config.host, port=config.port, linuxpath=config.linuxpath, reread_on_query=config.reread_on_query, ssl_enabled=config.ssl_enabled)
    server_thread = threading.Thread(target=server.start, daemon=True)
    server_thread.start()
    time.sleep(1)  # Give the server a moment to start
    yield server
    server.server_socket.close()

@pytest.fixture
def client():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    yield client_socket
    client_socket.close()

def test_empty_query(server, client):
    print("Running test_empty_query")
    client.connect(('localhost', 12345))
    client.sendall(b'\x00')
    response = client.recv(1024).decode('utf-8')
    print(f"Response: {response}")
    assert response.strip() == 'ERROR: Empty query'

def test_string_exists(server, client):
    print("Running test_string_exists")
    with open('./200k.txt', 'w') as f:
        f.write('test_string\n')
    
    client.connect(('localhost', 12345))
    client.sendall(b'test_string')
    response = client.recv(1024).decode('utf-8')
    print(f"Response: {response}")
    assert response.strip() == 'STRING EXISTS'

    os.remove('./200k.txt')

def test_string_not_found(server, client):
    print("Running test_string_not_found")
    with open('./200k.txt', 'w') as f:
        f.write('some_other_string\n')
    
    client.connect(('localhost', 12345))
    client.sendall(b'test_string')
    response = client.recv(1024).decode('utf-8')
    print(f"Response: {response}")
    assert response.strip() == 'STRING NOT FOUND'

    os.remove('./200k.txt')

def test_payload_too_large(server, client):
    print("Running test_payload_too_large")
    large_payload = b'a' * 2048
    client.connect(('localhost', 12345))
    client.sendall(large_payload)
    response = client.recv(1024).decode('utf-8')
    print(f"Response: {response}")
    assert response.strip() == 'ERROR: Payload too large'

def test_file_not_found(server, client):
    print("Running test_file_not_found")
    if os.path.exists('./200k.txt'):
        os.remove('./200k.txt')
    
    client.connect(('localhost', 12345))
    client.sendall(b'test_string')
    response = client.recv(1024).decode('utf-8')
    print(f"Response: {response}")
    assert response.strip() == 'ERROR: File not found'

def test_ssl_error_handling():
    print("Running test_ssl_error_handling")
    config = MockConfig(ssl=True)
    server = FileSearchServer(host=config.host, port=config.port, linuxpath=config.linuxpath, reread_on_query=config.reread_on_query, ssl_enabled=config.ssl_enabled)
    server_thread = threading.Thread(target=server.start, daemon=True)
    server_thread.start()
    time.sleep(1)

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        with pytest.raises(ssl.SSLError):
            ssl.wrap_socket(client_socket).connect((config.host, config.port))
    finally:
        server.server_socket.close()
        client_socket.close()
