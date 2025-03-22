# Use a base Python image
FROM python:3.11

# Install Tesseract and manually create the tessdata directory
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libtesseract-dev \
    tesseract-ocr-eng && \
    mkdir -p /usr/share/tesseract-ocr/4.00/tessdata/ && \
    cp -r /usr/share/tesseract-ocr/tessdata/* /usr/share/tesseract-ocr/4.00/tessdata/ && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Verify installation
RUN tesseract --version && ls -lah /usr/share/tesseract-ocr/4.00/tessdata/

# Set the TESSDATA_PREFIX environment variable
ENV TESSDATA_PREFIX="/usr/share/tesseract-ocr/4.00/tessdata/"

# Set the working directory
WORKDIR /app

# Copy project files
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port Flask runs on
EXPOSE 5000

# Start the Flask application
CMD ["python", "app.py"]
