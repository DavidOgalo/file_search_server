#!/bin/bash

# Install necessary packages
sudo apt update
sudo apt install -y python3 python3-pip git openssl

# Clone the GitHub repository
echo "Cloning the repository..."
git clone https://github.com/DavidOgalo/file_search_server.git
cd file_search_server

# Download the data file
echo "Downloading the data file..."
wget https://www.dropbox.com/scl/fi/ripx1gu2s5w48pklln75f/200k.txt?rlkey=j7l29szvqw0hlyyfhw4i4b1on&e=9&dl=0 -O 200k.txt

# Set up the configuration file
echo "Creating the configuration file..."
cat <<EOL > config.ini
[Settings]
linuxpath = $(pwd)/200k.txt
REREAD_ON_QUERY = true

[Server]
host = localhost
port = 12345
ssl_enabled = true
EOL

# Generate SSL certificate and key
echo "Generating SSL certificate and key..."
openssl genpkey -algorithm RSA -out server.key -pkeyopt rsa_keygen_bits:2048
openssl req -new -key server.key -out server.csr
openssl x509 -req -days 365 -in server.csr -signkey server.key -out server.crt

echo "Setup complete!"
