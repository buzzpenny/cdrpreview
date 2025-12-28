# Use a lightweight Python image
FROM python:3.9-slim

# Install Inkscape and a comprehensive set of fonts
# fonts-dejavu, fonts-noto, and ghostscript help with missing elements and rendering text
RUN apt-get update && apt-get install -y \
    inkscape \
    fonts-liberation \
    fonts-dejavu \
    fonts-noto \
    ghostscript \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the app
COPY . .

# Expose the port
EXPOSE 5000

# Command to run the app using Gunicorn (Production server)
# UPDATED: We use --workers 1 to save RAM on free tier hosting
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "1", "--threads", "8", "--timeout", "120", "app:app"]
