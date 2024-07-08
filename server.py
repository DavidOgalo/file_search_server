import socket
import threading
import configparser
import ssl
import logging
import time

# Load configuration settings
config = configparser.ConfigParser()
config.read('config.ini')

# Get the path to the file and the REREAD_ON_QUERY option with default values
linuxpath = config.get('Settings', 'linuxpath', fallback='./200k.txt')
reread_on_query = config.getboolean('Settings', 'REREAD_ON_QUERY', fallback=True)

# Get server host and port from the configuration
HOST = config.get('Server', 'host', fallback='localhost')
PORT = config.getint('Server', 'port', fallback=12345)
SSL_ENABLED = config.getboolean('Server', 'ssl_enabled', fallback=True)

# Set up logging to track server activity
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

class FileSearchServer:
    def __init__(self, host=HOST, port=PORT, linuxpath=linuxpath, reread_on_query=reread_on_query, ssl_enabled=SSL_ENABLED):
        self.host = host
        self.port = port
        self.linuxpath = linuxpath
        self.reread_on_query = reread_on_query
        self.ssl_enabled = ssl_enabled
        self.server_socket = None
        self.ssl_context = None
        self.data = None  # Cache the file data if reread_on_query is False

    def setup_server(self):
        """Set up the server with or without SSL based on configuration."""
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        logger.info(f'Server listening on {self.host}:{self.port}')

        if self.ssl_enabled:
            self.ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            self.ssl_context.load_cert_chain(certfile='server.crt', keyfile='server.key')
            logger.info('SSL enabled: Using SSL for secure connections')
        else:
            logger.info('SSL not enabled: Using plain TCP connections')

    def handle_client(self, client_socket):
        """Handle client connections and process their queries."""
        client_ip = client_socket.getpeername()[0]
        start_time = time.time()
        try:
            if self.ssl_enabled:
                with self.ssl_context.wrap_socket(client_socket, server_side=True) as ssl_socket:
                    data = ssl_socket.recv(1024).decode('utf-8').rstrip('\x00')
                    logger.debug(f"Received query: {data}")
                    response = self.process_query(data)
                    ssl_socket.sendall(response.encode('utf-8'))
            else:
                data = client_socket.recv(1024).decode('utf-8').rstrip('\x00')
                logger.debug(f"Received query: {data}")
                response = self.process_query(data)
                client_socket.sendall(response.encode('utf-8'))

            execution_time = time.time() - start_time
            logger.debug(f"Query: {data}, Requesting IP: {client_ip}, Execution Time: {execution_time:.4f}s, Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")

        except Exception as e:
            logger.error(f'Error handling client: {e}')
        finally:
            client_socket.close()

    def process_query(self, query):
        """Process the query received from the client."""
        if not query:
            return 'ERROR: Empty query\n'
        if len(query) > 1024:
            return 'ERROR: Payload too large\n'
        try:
            if self.reread_on_query or not self.data:
                with open(self.linuxpath, 'r') as file:
                    data = file.readlines()
                    if not self.reread_on_query:
                        self.data = data
            else:
                data = self.data

            results = [line.strip() for line in data if line.strip() == query]
            return 'STRING EXISTS\n' if results else 'STRING NOT FOUND\n'
        except FileNotFoundError:
            logger.error(f'File not found: {self.linuxpath}')
            return 'ERROR: File not found\n'
        except Exception as e:
            logger.error(f'Error processing query: {e}')
            return 'ERROR: Internal server error\n'

    def start(self):
        """Start the server and handle incoming connections."""
        self.setup_server()
        while True:
            try:
                client_socket, client_address = self.server_socket.accept()
                logger.info(f'Connection from {client_address}')
                client_thread = threading.Thread(target=self.handle_client, args=(client_socket,))
                client_thread.start()
            except Exception as e:
                logger.error(f'Error accepting connections: {e}')
                break

if __name__ == '__main__':
    server = FileSearchServer()
    server.start()
