# File Search Server

## Description

This project implements a Python-based server application designed to efficiently search through a large text file. The server is multi-threaded and supports SSL, enabling secure communication with multiple clients simultaneously. The project includes configuration management and logging, and benchmarks various file-search algorithms to determine the most efficient approach for querying the data.

## Table of Contents

- [Description](#description)
- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Contributing](#contributing)
- [License](#license)

## Features

- Multi-threaded server for handling concurrent client connections.
- SSL support for secure communication.
- Configuration management via `config.ini`.
- Logging to track server activity and client interactions.
- Benchmarking of different file-search algorithms.

## Requirements

- Python 3.x
- `socket` module (standard library)
- `threading` module (standard library)
- `configparser` module (standard library)
- `ssl` module (standard library)
- `logging` module (standard library)
- Git

## Installation

1. **Clone the repository:**
    ```sh
    git clone https://github.com/DavidOgalo/file_search_server.git
    cd file_search_server
    ```

2. **Download the data file:**
    ```sh
    wget https://www.dropbox.com/scl/fi/ripx1gu2s5w48pklln75f/200k.txt?rlkey=j7l29szvqw0hlyyfhw4i4b1on&e=9&dl=0 -O 200k.txt
    ```

3. **Run the setup script:**
    ```sh
    ./setup.sh
    ```

## Usage

1. **Run the server:**
    ```sh
    python3 server.py
    ```

2. **Connect to the server from a client:**
    - Use a socket client to send queries to the server.
    - The server listens on `localhost` and port `12345`.

3. **Example client script:**
    ```python
    import socket

    HOST = 'localhost'
    PORT = 12345

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.sendall(b'your query here')
        data = s.recv(1024)

    print('Received', repr(data))
    ```

## Configuration

Edit the `config.ini` file to configure the server settings:

```ini
[Settings]
linuxpath = /path/to/your/200k.txt
REREAD_ON_QUERY = true