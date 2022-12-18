#! /bin/bash

# Check if Python is installed
if command -v python3 &>/dev/null; then
  if [ -d "venv" ]; then
    # Check if a virtual environment is active
    if [[ -n "$VIRTUAL_ENV" ]]; then
        # Run the Python script
        python app.py
    else
      # Activate the virtual environment
      source venv/bin/activate

      # Run the Python script
      python app.py
    fi
  else
    echo "Virtual environment not created, try running ./install_requirements.sh"
  fi 
else
  # Display an error message if Python is not found
  echo "Error: This program needs Python to run, to install check out https://www.python.org/downloads/" >&2
fi