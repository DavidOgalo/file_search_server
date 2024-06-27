import socket
import threading
import configparser
import ssl
import logging

# Read configuration from config.ini
config = configparser.ConfigParser()
config.read('config.ini')
linuxpath = config['Settings']['linuxpath']
reread_on_query = config['Settings'].getboolean('REREAD_ON_QUERY')

# Set up logging to track server activity
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Server configuration settings
HOST = 'localhost'
PORT = 12345
BUFFER_SIZE = 1024
SSL_ENABLED = True  # Configure SSL if required

def handle_client(conn, addr):
    # """Handles incoming client connections."""
    logging.info(f'Connected by {addr}')
    with conn:
        while True:
            data = conn.recv(BUFFER_SIZE)
            if not data:
                break
            query = data.decode('utf-8')
            logging.info(f'Received query: {query}')
            result = search_file(query)
            conn.sendall(result.encode('utf-8'))
    logging.info(f'Connection with {addr} closed')

def search_file(query):
    # """Searches the file for the given query. Placeholder for actual search logic."""
    return f'Search result for query: {query}'

def main():
    # """Main function to set up and start the server."""
    context = None
    if SSL_ENABLED:
        context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        context.load_cert_chain(certfile='server.crt', keyfile='server.key')

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        logging.info(f'Server listening on {HOST}:{PORT}')
        while True:
            conn, addr = s.accept()
            if SSL_ENABLED:
                conn = context.wrap_socket(conn, server_side=True)
            threading.Thread(target=handle_client, args=(conn, addr)).start()

if __name__ == '__main__':
    main()
