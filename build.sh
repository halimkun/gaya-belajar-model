#!/bin/bash

# Set the error handling mode
set -e

# Get today's date in YYYYMMDD format
TODAY=$(date +"%Y%m%d")

# Run docker compose commands with error handling
{
    echo "Stopping and removing existing containers..."
    docker compose down

    echo "Building the image with tag gaya-belajar-model:$TODAY..."
    # Use build context to set image tag via the docker-compose.yml file
    sed -i "s/image: gaya-belajar-model:.*/image: gaya-belajar-model:$TODAY/" docker-compose.yml
    docker compose build
} || {
    echo "Error during Docker build or down operation."
    exit 1
}

# Confirmation prompt
read -p "Do you want to run the container now? (yes/no) " choice
if [[ "$choice" == "yes" ]]; then
    {
        echo "Starting the container..."
        docker compose up -d
        echo "Container is running with tag gaya-belajar-model:$TODAY"
    } || {
        echo "Error during starting the container."
        exit 1
    }
else
    echo "Build completed. Run 'docker compose up -d' to start the container."
fi
