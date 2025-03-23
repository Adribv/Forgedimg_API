#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install system dependencies (Tesseract OCR and its dependencies)
apt-get update
apt-get install -y tesseract-ocr tesseract-ocr-eng libtesseract-dev libleptonica-dev libzbar0

# Create upload directory
mkdir -p uploads

# Install Python dependencies
pip install -U pip
pip install -r requirements.txt