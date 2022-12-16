#!/bin/bash

echo "Creting virtual environment and installing requirements"
if command -v python3 &>/dev/null; then
  # Create a virtual environment
  python3 -m venv venv

  # Activate the virtual environment
  source env/bin/activate

  # Install the required packages from the requirements file
  pip install -r requirements.txt
fi