FROM python:3.9-slim

# Create user for FTP access
RUN useradd -m -s /bin/bash ctf && \
    echo "ctf:password" | chpasswd

# Create flag file
RUN mkdir -p /opt/secret && \
    echo "CTF{v5ftpd_b4ckd00r_exp10it3d}" > /opt/secret/flag.txt && \
    chmod 644 /opt/secret/flag.txt

# Copy Python FTP server with backdoor implementation
COPY backdoor_ftp.py /backdoor_ftp.py
RUN chmod +x /backdoor_ftp.py

# Expose ports
EXPOSE 21/tcp
EXPOSE 6200/tcp

# Start the Python FTP server
CMD ["python3", "/backdoor_ftp.py"]