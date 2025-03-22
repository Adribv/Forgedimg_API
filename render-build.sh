#!/bin/bash

echo "Updating system..."
sudo apt-get update

echo "Installing Tesseract OCR and dependencies..."
sudo apt-get install -y tesseract-ocr libtesseract-dev

echo "Build complete."
