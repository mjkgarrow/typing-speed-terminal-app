#!/bin/bash

echo "Creting virtual environment and installing requirements"
if command -v python3 &>/dev/null; then
  # Create a virtual environment
  python3 -m venv venv

  # Activate the virtual environment
  source env/bin/activate

  # Update pip (seems to need it)
  pip install --upgrade pip

  # Install the required packages from the requirements file
  pip install -r requirements.txt  
else
  # Display an error message if Python is not found
  echo "Error: This program runs on Python, which isn't installed on this machine. To install Python, check out https://installpython3.com/'" >&2
fi