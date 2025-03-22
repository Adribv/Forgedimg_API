# Use a Python image
FROM python:3.11

# Install Tesseract and manually set the correct tessdata path
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libtesseract-dev \
    tesseract-ocr-eng && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Find the correct tessdata directory
RUN TESSDATA_DIR=$(find /usr/share -type d -name "tessdata" | head -n 1) && \
    echo "TESSDATA_DIR found at: $TESSDATA_DIR" && \
    ln -s $TESSDATA_DIR /usr/share/tesseract-ocr/4.00/tessdata/

# Set the correct TESSDATA_PREFIX
ENV TESSDATA_PREFIX="/usr/share/tesseract-ocr/4.00/tessdata/"

# Set working directory
WORKDIR /app

# Copy project files
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port Flask runs on
EXPOSE 5000

# Start the Flask application
CMD ["python", "app.py"]
