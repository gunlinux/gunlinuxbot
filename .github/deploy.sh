#!/bin/bash

REPO_DIR="~loki/projects/gunlinuxbot"
BRANCH="master"

# Navigate to the repository directory
cd $REPO_DIR || exit

# Fetch and reset changes from the remote repository
git fetch --all
git reset --hard origin/$BRANCH

# Optionally run build or install commands here if needed
# e.g., npm install, yarn install for Node.js projects

# Restart services using sudo
sudo systemctl restart twitch_sender.service

echo "Deployment completed successfully."
