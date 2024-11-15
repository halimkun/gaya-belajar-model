#!/bin/bash

# Get today's date in YYYYMMDD format
TODAY=$(date +"%Y%m%d")

# Docker build with a tag that includes today's date
docker compose down
docker compose build --tag gaya-belajar-model:$TODAY

# Confirmation prompt
read -p "Do you want to run the container now? (yes/no) " choice
if [[ "$choice" == "yes" ]]; then
    docker compose up -d
    echo "Container is running with tag gaya-belajar-model:$TODAY"
else
    echo "Build completed. Run 'docker compose up -d' to start the container."
fi
