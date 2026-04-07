# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /app

# Install dependencies
COPY pyproject.toml /app/
RUN pip install --no-cache-dir -e .

# Copy the rest of the application's code
COPY . /app/

# Make the run script executable
RUN chmod +x /app/scripts/run.sh

# Expose the port the app runs on
EXPOSE 8000

# Specify the command to run on container startup
CMD ["/app/scripts/run.sh"]
