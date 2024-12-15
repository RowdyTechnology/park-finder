# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install tzdata and set the timezone to Phoenix
RUN apt-get update && apt-get install -y tzdata && \
    ln -snf /usr/share/zoneinfo/America/Phoenix /etc/localtime && \
    echo "America/Phoenix" > /etc/timezone && \
    apt-get clean

# Expose port 8086 for the Flask app
EXPOSE 8086

# Define environment variables
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=8086

# Set the timezone environment variable
ENV TZ=America/Phoenix

# Run the application
CMD ["flask", "run"]
