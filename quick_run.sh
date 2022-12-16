#! /bin/bash

# Check if Python is installed
if ! command -v python3 &>/dev/null; 
then
  # Run the Python script
  python3 ./app.py
else
  # Display an error message if Python is not found
  echo "Error: This program runs on Python, which. To install Python, check out https://installpython3.com/'" >&2
fi