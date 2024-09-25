# Use an official Python runtime as a parent image
FROM python:3.11.9-bullseye

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# The application code will be mounted at runtime, so we don't need to COPY it here

# Run miner.py when the container launches
CMD ["python", "miner/miner.py"]