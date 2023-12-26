#!/bin/bash

# Run any setup steps or pre-processing tasks here
echo "Loading data into Neo4j..."

# Run your Python script
python etl/healthcare_bulk_csv_write.py

# Start the main application
uvicorn main:app --host 0.0.0.0 --port 8000