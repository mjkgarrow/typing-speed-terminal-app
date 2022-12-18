#!/bin/bash

echo "Creating virtual environment and installing requirements"

# Check if Python is installed
if command -v python3 &>/dev/null; then
  # Check if a folder called 'venv' already exists
  if [ -d "venv" ]; then
    # Check if the virtual environment is active
    if [[ -n "$VIRTUAL_ENV" ]]; then
      # Get Python version numbers (major.minor)
      vermajor=$(python -c"import sys; print(sys.version_info.major)")
      verminor=$(python -c"import sys; print(sys.version_info.minor)")

     # Check python version number (must be greater that 3.7)
      if [ $vermajor -eq 3 ] && [ $verminor -gt 7 ]; then
        # Install the required packages from the requirements file
        pip3 install -r requirements.txt | grep -v 'already satisfied'

        # Update pip (it seems to need it)
        pip install --upgrade pip
      else 
        echo "Error: This program needs Python 3.8+ to run, to install check out https://www.python.org/downloads/"
      fi 
    else
      # Activate the virtual environment
      source venv/bin/activate

      # Install the required packages from the requirements file
      pip3 install -r requirements.txt | grep -v 'already satisfied'

      # Update pip (it seems to need it)
      pip install --upgrade pip
    fi
  else
    # Create a virtual environment
    python3 -m venv venv

    # Activate the virtual environment
    source venv/bin/activate

    # Install the required packages from the requirements file
    pip3 install -r requirements.txt | grep -v 'already satisfied'

    # Update pip (it seems to need it)
    pip install --upgrade pip
  fi 
else
  # Display an error message if Python is not found
  echo "Error: This program needs Python to run, to install check out https://www.python.org/downloads/"
  exit
fi
echo "Virtual environment created and requirments installed, to play run ./run_app.sh"