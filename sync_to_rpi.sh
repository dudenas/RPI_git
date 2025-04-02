#!/bin/bash

# Configuration
RPI_IP="172.20.10.5"
RPI_USER="pi"
RPI_PASSWORD="labas"  # Only used once during SSH key setup
RPI_PATH="/home/pi/Desktop"  # Destination folder on Raspberry Pi

# Colors for better readability
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# Print colored messages
echo_color() {
    echo -e "${1}${2}${NC}"
}

echo_color "$BLUE" "===== RPI_git Sync Tool ====="

# Check if SSH key is already copied to the Raspberry Pi
SSH_TEST=$(ssh -o BatchMode=yes -o ConnectTimeout=5 -o StrictHostKeyChecking=no "$RPI_USER@$RPI_IP" "echo Connected" 2>&1)
SSH_AUTH_WORKS=$?

# If SSH key authentication doesn't work yet, let's set it up
if [ $SSH_AUTH_WORKS -ne 0 ]; then
    echo_color "$YELLOW" "SSH key authentication not set up yet."
    
    # Check if SSH key exists
    if [ ! -f ~/.ssh/id_rsa ]; then
        echo_color "$BLUE" "No SSH key found. Creating a new SSH key..."
        ssh-keygen -t rsa -N "" -f ~/.ssh/id_rsa
        
        if [ $? -ne 0 ]; then
            echo_color "$RED" "Failed to create SSH key."
            exit 1
        fi
        echo_color "$GREEN" "SSH key created successfully!"
    fi
    
    # Install sshpass if needed
    if ! command -v sshpass &> /dev/null; then
        echo_color "$BLUE" "Installing sshpass (needed only for initial setup)..."
        brew install hudochenkov/sshpass/sshpass
    fi
    
    # Copy SSH key to Raspberry Pi
    echo_color "$YELLOW" "==============================================================="
    echo_color "$YELLOW" "You'll need to enter your password just this ONE TIME:"
    echo_color "$YELLOW" "After this setup, you won't need to enter your password again."
    echo_color "$YELLOW" "==============================================================="
    
    ssh-copy-id -o StrictHostKeyChecking=no "$RPI_USER@$RPI_IP"
    
    if [ $? -eq 0 ]; then
        echo_color "$GREEN" "✅ SSH key copied successfully!"
    else
        echo_color "$RED" "Failed to copy SSH key to Raspberry Pi."
        echo_color "$RED" "Please make sure your Raspberry Pi is powered on and connected to the network."
        exit 1
    fi
else
    echo_color "$GREEN" "✅ SSH key already set up! No password needed."
fi

# Test SSH connection
echo_color "$BLUE" "Testing connection to Raspberry Pi..."
ssh -o StrictHostKeyChecking=no -o ConnectTimeout=5 "$RPI_USER@$RPI_IP" "echo Connected" &>/dev/null
if [ $? -ne 0 ]; then
    echo_color "$RED" "❌ Could not connect to Raspberry Pi at $RPI_IP"
    exit 1
fi
echo_color "$GREEN" "✅ Connected to Raspberry Pi"

# Create directories via SSH first (more reliable than SFTP mkdir -p)
echo_color "$BLUE" "Creating directories on Raspberry Pi..."
DIRS_TO_CREATE=$(find . -type d -not -path "*/\.*" | grep -v "^\.$")
for dir in $DIRS_TO_CREATE; do
    target_dir="${dir:2}"  # Remove ./ from beginning
    echo_color "$BLUE" "  Creating: $target_dir"
    ssh -o StrictHostKeyChecking=no "$RPI_USER@$RPI_IP" "mkdir -p '$RPI_PATH/$target_dir'" &>/dev/null
done

# Create SFTP batch file for file transfers only
BATCH_FILE=$(mktemp)
echo "cd $RPI_PATH" > "$BATCH_FILE"

# Add all files (excluding .git and .DSStore)
echo_color "$BLUE" "Preparing file list for transfer..."
find . -type f -not -path "*/\.*" -not -path "*/\.git/*" -not -name ".DS_Store" -not -name "sync_to_rpi.sh" | while read -r file; do
    target_file="${file:2}"  # Remove ./ from the beginning
    target_dir=$(dirname "$target_file")
    
    # Add cd commands to navigate to the correct directory
    if [ "$target_dir" != "." ]; then
        echo "cd $RPI_PATH/$target_dir" >> "$BATCH_FILE"
        echo "put \"$file\" \"$(basename "$target_file")\"" >> "$BATCH_FILE"
        echo "cd $RPI_PATH" >> "$BATCH_FILE"
    else
        echo "put \"$file\" \"$target_file\"" >> "$BATCH_FILE"
    fi
    
    echo_color "$BLUE" "  Adding: $target_file"
done

echo "bye" >> "$BATCH_FILE"

# Execute SFTP transfer
echo_color "$BLUE" "Starting SFTP transfer..."
sftp -o StrictHostKeyChecking=no -b "$BATCH_FILE" "$RPI_USER@$RPI_IP"

if [ $? -eq 0 ]; then
    echo_color "$GREEN" "✅ Files successfully transferred to Raspberry Pi!"
    echo_color "$GREEN" "Files are now available at: $RPI_PATH"
else
    echo_color "$RED" "❌ Transfer failed. Check your connection and try again."
    
    # Display the SFTP batch file for debugging
    echo_color "$YELLOW" "SFTP batch file contents:"
    cat "$BATCH_FILE"
fi

# Clean up
rm "$BATCH_FILE"
echo_color "$BLUE" "===== Sync Complete =====" 