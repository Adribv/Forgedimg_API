# Use a base image that includes Tesseract
FROM python:3.11

# Install system dependencies (including Tesseract)
RUN apt-get update && apt-get install -y tesseract-ocr libtesseract-dev

# Set the working directory
WORKDIR /app

# Copy your project files
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set environment variables
ENV TESSDATA_PREFIX=/usr/share/tesseract-ocr/4.00/tessdata

# Expose the port Flask runs on
EXPOSE 5000

# Start the Flask application
CMD ["python", "app.py"]
