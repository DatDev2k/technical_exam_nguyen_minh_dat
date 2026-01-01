# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . .

# Install dependencies (only pytest for running tests, main app uses standard lib)
RUN pip install --no-cache-dir pytest

# Define entrypoint to run the aggregator
ENTRYPOINT ["python", "aggregator.py"]

# Default arguments (can be overridden)
CMD ["--help"]
