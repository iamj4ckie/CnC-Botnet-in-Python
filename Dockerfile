# Use an official Python image as the base
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Create the working directory explicitly
RUN mkdir -p /app

# Copy your application files
COPY . /app

# Rename hosts.txt.sample to hosts.txt during build
RUN cp /app/hosts.txt.sample /app/hosts.txt

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install any additional system dependencies required by Fabric/Paramiko
RUN apt-get update && apt-get install -y --no-install-recommends \
    sshpass openssh-client && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Default command to keep the container running
CMD ["sleep", "infinity"]

