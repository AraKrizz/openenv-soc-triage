# Use an official Python runtime
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Copy the current directory contents into the container
COPY . /app

# Install the required libraries
RUN pip install --no-cache-dir openenv-core pydantic openai

# Start the web server from the new server folder
CMD ["uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "7860"]
