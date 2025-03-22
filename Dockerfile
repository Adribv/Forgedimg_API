# Use a base Python image
FROM python:3.11

# Install Tesseract and the English language model
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libtesseract-dev \
    tesseract-ocr-eng && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Find the correct Tesseract tessdata directory dynamically
RUN TESSDATA_DIR=$(find /usr/share -type d -name "tessdata" | head -n 1) && \
    echo "TESSDATA_DIR found at: $TESSDATA_DIR" && \
    echo "export TESSDATA_PREFIX=$TESSDATA_DIR" >> ~/.bashrc

# Set the environment variable permanently
ENV TESSDATA_PREFIX="/usr/share/tesseract-ocr/5/tessdata/"

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
