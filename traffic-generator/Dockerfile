# Use a lightweight Python base image
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Install the required requests library
RUN pip install --no-cache-dir requests

# Copy the Python script into the container
COPY traffic_generator.py .

# Use ENTRYPOINT so arguments passed to 'docker run' are forwarded to the script
ENTRYPOINT ["python3", "traffic_generator.py"]

# Default argument if none is provided
CMD ["--count", "1500"]