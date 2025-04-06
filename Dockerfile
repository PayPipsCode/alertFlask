# Use the official slim Python image
FROM python:3.10-slim

# Prevent Python from writing pyc files to disk and buffer stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory to /app
WORKDIR /app

# Copy everything into the container
COPY . .

WORKDIR /app

# Install Python dependencies
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Expose the port provided by Railway (Railway sets the PORT env variable)
EXPOSE ${PORT}

# Start the Flask app. Make sure run.py is set to listen on 0.0.0.0 and uses PORT env variable.
CMD ["python", "run.py"]
