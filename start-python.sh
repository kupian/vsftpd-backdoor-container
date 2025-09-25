#!/bin/bash

# Start the Python FTP server
python3 /backdoor_ftp.py

# The Python script has its own infinite loop, so we don't need 
# to add anything here to keep the container running