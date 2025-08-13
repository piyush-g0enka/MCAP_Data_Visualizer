# Use an official Python runtime as a parent image
FROM python:3.9

# Set the working directory in the container
WORKDIR /app

# Copy the script and MCAP file to the container
COPY main.py .
COPY recording.mcap .

# Install required Python dependencies
RUN pip install numpy matplotlib mcap

# Set the command to run the script
CMD ["python3", "main.py"]
