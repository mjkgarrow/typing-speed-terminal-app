#!/bin/bash



echo "Creating virtual environment and installing requirements"

# Check if Python is installed
if command -v python3 &>/dev/null; then
  # Check if a folder called 'venv' already exists
  if [ -d "venv" ]; then
    # Check if the virtual environment is active
    if [[ -n "$VIRTUAL_ENV" ]]; then
      # Install the required packages from the requirements file
      pip install -r requirements.txt  
    else
      # Activate the virtual environment
      source venv/bin/activate

      # Install the required packages from the requirements file
      # Blocks "already installed" notifications
      pip install -r requirements.txt | grep -v 'already satisfied'
    fi
  else
    # Create a virtual environment
    python3 -m venv venv

    # Activate the virtual environment
    source venv/bin/activate

    # Update pip (seems to need it)
    pip install --upgrade pip

    # Install the required packages from the requirements file
    pip install -r requirements.txt  
  fi 
else
  # Display an error message if Python is not found
  echo "Error: This program needs Python to run, To install Python check out https://www.python.org/downloads/" >&2
fi
echo "Virtual environment created and requirments installed, run ./run_app.sh to play game"