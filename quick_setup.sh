#! /bin/bash


echo "Creating virtual environment, installing requirements and running game"

# Check if Python is installed
if command -v python3 &>/dev/null; then
  # Check if a folder called 'venv' already exists
  if [ -d "venv" ]; then
    # Check if the virtual environment is active
    if [[ -n "$VIRTUAL_ENV" ]]; then
      # Install the required packages from the requirements file
      pip install -r requirements.txt | grep -v 'already satisfied'  
    else
      # Activate the virtual environment
      source venv/bin/activate

      # Install the required packages from the requirements file
      pip install -r requirements.txt | grep -v 'already satisfied'  

      # Run the Python script
      python app.py
    fi
  else
    # Create a virtual environment
    python3 -m venv venv

    # Activate the virtual environment
    source venv/bin/activate

    # Install the required packages from the requirements file
    pip install -r requirements.txt

    # Run the Python script
    python app.py
  fi 
else
  # Display an error message if Python is not found
  echo "Error: This program needs Python to run, to install check out https://www.python.org/downloads/" >&2
fi