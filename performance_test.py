import socket
import ssl
import time
import threading
import configparser

config = configparser.ConfigParser()
config.read('config.ini')

HOST = config.get('Server', 'host', fallback='localhost')
PORT = config.getint('Server', 'port', fallback=12345)
SSL_ENABLED = config.getboolean('Server', 'ssl_enabled', fallback=True)
NUM_CLIENTS = 50  # Number of clients to simulate
QUERY_STRING = '11;0;23;11;0;20;5;0;' # provide query string

def client_task(query):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    if SSL_ENABLED:
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        with context.wrap_socket(client_socket, server_hostname=HOST) as ssl_socket:
            ssl_socket.connect((HOST, PORT))
            ssl_socket.sendall(query.encode('utf-8'))
            response = ssl_socket.recv(1024).decode('utf-8')
            print(f'Server response: {response}')
    else:
        client_socket.connect((HOST, PORT))
        client_socket.sendall(query.encode('utf-8'))
        response = client_socket.recv(1024).decode('utf-8')
        print(f'Server response: {response}')
    client_socket.close()

if __name__ == '__main__':
    threads = []
    start_time = time.time()
    for _ in range(NUM_CLIENTS):
        thread = threading.Thread(target=client_task, args=(QUERY_STRING,))
        thread.start()
        threads.append(thread)
    for thread in threads:
        thread.join()
    end_time = time.time()
    print(f'Total execution time for {NUM_CLIENTS} clients: {end_time - start_time:.4f} seconds')
