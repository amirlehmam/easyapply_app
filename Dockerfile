# Use official Python slim image
FROM python:3.10-slim

# Install Chromium and dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        chromium-driver \
        chromium \
        fonts-liberation \
        libasound2 \
        libatk-bridge2.0-0 \
        libatk1.0-0 \
        libc6 \
        libcairo2 \
        libcups2 \
        libdbus-1-3 \
        libdrm2 \
        libgbm1 \
        libgtk-3-0 \
        libnspr4 \
        libnss3 \
        libx11-xcb1 \
        libxcomposite1 \
        libxdamage1 \
        libxrandr2 \
        xdg-utils \
        wget \
        ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Set environment variable for Chrome binary (used by Selenium)
ENV CHROME_BINARY=/usr/bin/chromium

WORKDIR /app
COPY . .

RUN pip install --upgrade pip && pip install -r requirements.txt

# Expose the port used by FastAPI/Gunicorn
EXPOSE 8000

# CMD should match your entrypoint (FastAPI, Gunicorn, etc.)
CMD ["python", "app.py"]