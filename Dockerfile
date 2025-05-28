# Use an official Python image
FROM python:3.11-slim

# Set the working directory
WORKDIR /app/program

# Copy application files
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the app's port (change if needed)
EXPOSE 5000

# Start the application
CMD ["python", "app.py"]

