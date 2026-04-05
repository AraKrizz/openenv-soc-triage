# Use an official Python runtime
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Copy the current directory contents into the container
COPY . /app

# Install the required libraries
RUN pip install --no-cache-dir openenv-core pydantic openai

# Command to run when the container starts (this satisfies the HF Space requirement)
CMD ["python", "-c", "import time; print('Environment is ready!'); time.sleep(86400)"]