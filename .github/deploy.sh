#!/bin/bash

REPO_DIR="/home/loki/projects/gunlinuxbot"
BRANCH="main"

# Navigate to the repository directory
cd $REPO_DIR || exit

# Fetch and reset changes from the remote repository
git fetch --all
git reset --hard origin/$BRANCH

# Optionally run build or install commands here if needed
# e.g., npm install, yarn install for Node.js projects

# Restart services using sudo
sudo systemctl restart donats_getter
sudo systemctl restart donats_worker
sudo systemctl restart twitch_getter
sudo systemctl restart twitch_sender
sudo systemctl restart twitch_worker
sudo systemctl restart beer_consumer

echo "Deployment completed successfully."
