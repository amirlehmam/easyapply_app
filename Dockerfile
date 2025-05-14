# Use an official Python base image
FROM python:3.10-slim

# Install Chromium and other dependencies
RUN apt-get update && \
    apt-get install -y chromium-driver chromium && \
    rm -rf /var/lib/apt/lists/*

# Set environment variable for Chrome binary
ENV CHROME_BINARY=/usr/bin/chromium

# Set workdir
WORKDIR /app

# Copy your code
COPY . .

# Install Python dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

# Expose the port your app runs on
EXPOSE 8000

# Start the app
CMD ["python", "app.py"]