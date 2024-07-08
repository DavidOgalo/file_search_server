import socket
import ssl
import configparser
import logging

# Load configuration settings
config = configparser.ConfigParser()
config.read('config.ini')

# Get server host, port, and SSL configuration
HOST = config.get('Server', 'host', fallback='localhost')
PORT = config.getint('Server', 'port', fallback=12345)
SSL_ENABLED = config.getboolean('Server', 'ssl_enabled', fallback=True)

# Set up logging to track client activity
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

class FileSearchClient:
    def __init__(self, host=HOST, port=PORT, ssl_enabled=SSL_ENABLED):
        self.host = host
        self.port = port
        self.ssl_enabled = ssl_enabled
        self.ssl_context = None

    def setup_ssl(self):
        """Set up SSL context if SSL is enabled."""
        if self.ssl_enabled:
            self.ssl_context = ssl.create_default_context()
            self.ssl_context.check_hostname = False
            self.ssl_context.verify_mode = ssl.CERT_NONE
            logger.info('SSL enabled: Using SSL for secure connections')
        else:
            logger.info('SSL not enabled: Using plain TCP connections')

    def send_query(self, query):
        """Send a query to the server and return the response."""
        if not query.strip():
            logger.error('Error: Empty query string')
            return 'ERROR: Empty query'
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            
            if self.ssl_enabled:
                with self.ssl_context.wrap_socket(client_socket, server_hostname=self.host) as ssl_socket:
                    ssl_socket.connect((self.host, self.port))
                    logger.info(f'Connected to server at {self.host}:{self.port}')
                    ssl_socket.sendall(query.encode('utf-8'))
                    response = ssl_socket.recv(1024).decode('utf-8')
                    logger.info(f'Received response: {response}')
                    return response
            else:
                client_socket.connect((self.host, self.port))
                logger.info(f'Connected to server at {self.host}:{self.port}')
                client_socket.sendall(query.encode('utf-8'))
                response = client_socket.recv(1024).decode('utf-8')
                logger.info(f'Received response: {response}')
                return response

        except Exception as e:
            logger.error(f'Error communicating with server: {e}')
            return 'ERROR: Communication failed\n'
        finally:
            client_socket.close()

if __name__ == '__main__':
    client = FileSearchClient()
    client.setup_ssl()

    while True:
        query = input('Enter the string to search for: ')
        if query.lower() == 'exit':
            break
        response = client.send_query(query)
        print(f'Server response: {response}')
