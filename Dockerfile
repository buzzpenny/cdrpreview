# Use a lightweight Python image
FROM python:3.9-slim

# Install Inkscape (Essential for CDR conversion)
# We also install fonts to ensure text renders somewhat correctly
RUN apt-get update && apt-get install -y \
    inkscape \
    fonts-liberation \
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
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--timeout", "120", "app:app"]
